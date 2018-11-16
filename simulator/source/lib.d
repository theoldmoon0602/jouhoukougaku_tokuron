module lib;

import std.random;


enum Team
{
  NO,
  A,
  B
}

/// 競技場に立つ哀れな高専生
class Agent
{
  public:
    uint x, y;  /// 座標
    uint id;    /// エージェント番号

    this(uint id, uint x, uint y)
    {
      this.id = id;
      this.x = x;
      this.y = y;
    }

    /// 所属チームを返す
    auto team() {   
      return (id <= 1) ? Team.A : Team.B;
    }
}

enum ActionName
{
  Invalid,
  Move,
  Remove,
}


enum Direction {
  LEFT_BOTTOM = 1,
  BOTTOM = 2,
  RIGHT_BOTTOM = 3,
  LEFT = 4,
  STAY = 5,
  RIGHT = 6,
  LEFT_UP = 7,
  UP = 8,
  RIGHT_UP = 9
}

/// 意思表示
class Action {
  public:
    ActionName action;
    Direction direction;

    this(ActionName action, Direction direction) {
      this.action = action;
      this.direction = direction;
    }
}

/// 競技
class Game
{
  public:
    uint w_size, h_size; /// 縦横サイズ
    int[][] panels;  /// 実際のパネルたち  
    Team[][] owners;  /// パネルの所有権を表す
    Agent[] agents;  /// 高専生
    uint turn;  /// 経過ターン数

    this(uint w_size, uint h_size)
      in
      {
        assert(2 <= w_size && w_size <= 12);
        assert(1 <= h_size && h_size <= 12);
      }
    do
    {
      this.w_size = w_size;
      this.h_size = h_size;

      this.panels = new int[][](h_size, w_size);
      this.owners = new Team[][](h_size, w_size);
      this.agents = [];

      this.turn = 0;
    }

    /// パネルの点数を初期化する
    /// FIXME: 偏り方を調整？
    void set_points(ref Random rng)
    {
      foreach (y; 0..(this.h_size + 1) / 2) {
        foreach (x; 0..((this.w_size + 1) / 2)) {
          int point = 0;
          if (dice(rng, 1, 1) == 0) {
            point = uniform(0, 17, rng);
          }
          else {
            point = uniform(-16, 17, rng);
          }

          this.panels[y][x] = point;
          this.panels[this.h_size - y - 1][x] = point;
          this.panels[y][this.w_size - x - 1] = point;
          this.panels[this.h_size - y - 1][this.w_size - x - 1] = point;
        }
      }
    }

    /// Agentを何処かに配置する
    void set_agents(ref Random rng)
      out
      {
        assert(this.agents.length == 4);
      }
    do
    {
      // ひとりめ
      uint x = uniform(0, this.w_size, rng);
      uint y = uniform(0, this.h_size, rng);
      Agent agent = new Agent(0, x, y);

      // ふたりめ
      uint x2 = x;
      uint y2 = y;
      while (x2 == x && y2 == y) {
        x2 = uniform(0, this.w_size, rng);
        y2 = uniform(0, this.h_size, rng);
      }
      Agent agent2 = new Agent(1, x2, y2);

      // 三人目、四人目
      Agent agent3, agent4;


      auto h_size = this.h_size - 1;
      auto w_size = this.w_size - 1;
      // 縦中央にいるとき横に並べる
      if (h_size - y == y) {

        // 横に並べたらかぶるときは諦めてやり直す
        if (y == y2 && w_size - x == x2) {
          this.set_agents(rng);
          return;
        }

        // 中央にいるときも諦める
        if (w_size - x == x) {
          this.set_agents(rng);
          return;
        }

        agent3 = new Agent(2, w_size - x, y);
      }
      else {
        agent3 = new Agent(2, w_size - x, h_size - y);
      }

      // 縦中央にいるとき横に並べる
      if (h_size - y2 == y2) {
        // これはありうる
        if (w_size - x2 == x2) {
          this.set_agents(rng);
          return;
        }

        agent4 = new Agent(3, w_size - x2, y2);
      }
      else {
        agent4 = new Agent(3, w_size - x2, h_size - y2);
      }

      this.agents = [agent, agent2, agent3, agent4];
    }

    /// 意思表示に基づいて行動を行う
    void do_actions(Action[] actions)
      in
      {
        assert(actions.length == this.agents.length);
      }
    do
    {
      auto move_x = [999, -1, 0, 1, -1, 0, 1, -1, 0, 1];
      auto move_y = [999, 1, 1, 1, 0, 0, 0, -1, -1, -1];

      ulong[] skip_agent_idxs = [];
      ulong[] next_xs = [];
      ulong[] next_ys = [];

      foreach (i, action; actions) {
        auto x = agents[i].x + move_x[action.direction];
        auto y = agents[i].y + move_y[action.direction];
        if (x < 0 || this.w_size <= x || y < 0 || this.h_size <= y) {
          skip_agent_idxs ~= i;
          next_xs ~= agents[i].x;
          next_ys ~= agents[i].y;
          continue;
        }
        next_xs ~= x;
        next_ys ~= y;

        if (action.action == ActionName.Move) {
          if (!(this.owners[y][x] == Team.NO || this.owners[y][x] == agents[i].team)) {
            skip_agent_idxs ~= i;
          }
        }
        else if (action.action == ActionName.Remove) {
          if (this.owners[y][x] == Team.NO || this.owners[y][x] == agents[i].team) {
            skip_agent_idxs ~= i;
          }
        }
      }

      import std.algorithm;
      actionLoop: foreach (i; 0..next_xs.length) {
        if (skip_agent_idxs.canFind(i)) {
          continue;
        }

        foreach (j; (i+1)..next_xs.length) {
          if (i ==j) { continue; }
          if (next_xs[i] == next_xs[j] && next_ys[i] == next_ys[j]) {
            if (actions[i].action == actions[j].action) {
              skip_agent_idxs ~= j;
              continue actionLoop;
            }
            else {
              if (actions[i].action == ActionName.Move) {
                skip_agent_idxs ~= j;
                continue actionLoop;
              }
            }
          }
        }

        uint x = cast(uint)next_xs[i];
        uint y = cast(uint)next_ys[i];
        if (actions[i].action == ActionName.Move) {
          this.agents[i].x = x;
          this.agents[i].y = y;
          this.owners[y][x] = this.agents[i].team;
        }
        else {
          this.owners[y][x] = Team.NO;
        }
      }
      this.turn++;
    }

    /// 現時点でのチームの点数を返す
    int get_score(Team team)
      in
      {
        assert(team != Team.NO);
      }
    do
    {
      int score = 0;

      // 取ったパネルの点数
      foreach (y; 0..this.h_size) {
        foreach (x; 0..this.w_size) {
          if (this.owners[y][x] == team) {
            score += this.panels[y][x];
          }
        }
      }

      // 囲んだ領域の点数
      auto flags = new int[][](this.h_size, this.w_size);  // 0: 未探訪, 1: 探訪済み
      auto dx = [0, -1, 1, 0];
      auto dy = [-1, 0, 0, 1];

      import std.range;
      import std.math;
      foreach (y; 0..this.h_size) {
        foreach (x; 0..this.w_size) {
          if (this.owners[y][x] == Team.NO && flags[y][x] == 0) {
            int tmp_score = 0;
            bool flag = true;  // falseになったら囲めてない
            int[][] q = [];  // 探索予定場所のqueue
            q ~= [x, y];

            while (q.length > 0) {
              auto p = q.front;
              q.popFront();
              auto x2 = p[0];
              auto y2 = p[1];
              if (x2 < 0 || this.w_size <= x2 || y2 < 0 || this.h_size <= y2) {
                flag = false;
                continue;
              }
              if (flags[y2][x2] != 0) {
                continue;
              }
              flags[y2][x2] = 1;

              if (this.owners[y2][x2] == team) {
                continue;
              }
              else {
                tmp_score += abs(this.panels[y2][x2]);
              }

              foreach (i; 0..4) {
                q ~= [x2 + dx[i], y2 + dy[i]];
              }
            }
            if (flag) {
              score += tmp_score;
              import std.stdio;
              debug stderr.writefln("x(%d, %d) -> %d", x, y, tmp_score);
            }

          }
        }
      }
      return score;
    }


    import std.json;

    /// 初期状態を返す
    JSONValue get_start_json()
    {
      JSONValue json;
      JSONValue[] agents = [];
      foreach (agent; this.agents) {
        agents ~= JSONValue([agent.x,agent.y]);
      }

      json["field_width"] = this.w_size;
      json["field_height"] = this.h_size;
      json["field"] = this.panels;
      json["agents"] = agents;
      json["scores"] = JSONValue([
          get_score(Team.A),
          get_score(Team.B)
      ]);

      return json;
    }


    /// 現在の状態をすべてJSONにして返す
    JSONValue get_status_json()
    {
      JSONValue json;

      JSONValue[] agents = [];
      foreach (agent; this.agents) {
        agents ~= JSONValue([agent.x,agent.y]);
      }
      json["turn"] = this.turn;
      json["agents"] = agents;
      json["owners"] = JSONValue(this.owners);
      json["scores"] = JSONValue([
          get_score(Team.A),
          get_score(Team.B)
      ]);
      return json;
    }

    /// JSON から Game の状態を復元
    static Game from_status_json(JSONValue status)
    {
      import std.conv;
      import std.stdio;
      auto w_size = status["field_width"].integer;
      auto h_size = status["field_height"].integer;

      Game game = new Game(cast(uint)w_size, cast(uint)h_size);

      game.turn = cast(uint)(status["turn"].integer);
      game.panels = new int[][](h_size, w_size);
      game.owners = new Team[][](h_size, w_size);
      game.agents = [];
      foreach (y, row; status["field"].array) {
        foreach (x, cell; row.array) {
          game.panels[y][x] = cast(int)cell.integer;
        }
      }

      foreach (y, row; status["owners"].array) {
        foreach (x, cell; row.array) {
          game.owners[y][x] = cell.integer.to!Team;
        }
      }

      foreach (i, agent; status["agents"].array) {
        game.agents ~= new Agent(cast(uint)i, cast(uint)agent.array[0].integer, cast(uint)agent.array[1].integer);
      }

      return game;
    }
}
