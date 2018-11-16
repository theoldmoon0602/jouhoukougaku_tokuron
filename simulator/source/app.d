import std.random;
import std.stdio;
import std.string;
import std.json;

import lib;

Action[] parse_actions() {
  string line = stdin.readln().strip();
  JSONValue j = parseJSON(line);

  Action[] actions = [];
  foreach (a; j["actions"].array) {
    ActionName name;
    int direction;
    if (a["action_direction"].integer == 5) {
      name = ActionName.Move;
      direction = 5;
    } else {
      name = (a["action_type"].integer == 1) ? ActionName.Remove : ActionName.Move;
      direction = cast(int)(a["action_direction"].integer);
    }

    actions ~= new Action(name, cast(Direction)direction);
  }
  return actions;
}

Game parse_status() {
  string line = stdin.readln().strip();
  JSONValue j = parseJSON(line);

  return Game.from_status_json(j);
}


void main(string[] args)
{
  if (args.length >= 2 && args[1] == "init") {
    Random rng = rndGen();
    Game game = new Game(uniform(8, 13, rng), uniform(8, 13, rng));
    game.set_points(rng);
    game.set_agents(rng);
    writeln(game.get_start_json());
    writeln(game.get_status_json());
  }
  else {
    Game game = parse_status();
    auto actions = parse_actions();
    game.do_actions(actions);
    writeln(game.get_status_json());
  }
}

