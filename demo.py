"""Run saved-policy episodes (value iteration by default) in the registered environment."""

import argparse
from policy_playback import CLI_POLICIES, load_policy, requested_action

import gymnasium as gym
import icy_gridworld  # Register the environment before gym.make.


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def nonnegative_integer(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episodes", type=positive_integer, default=1)
    parser.add_argument("--seed", type=nonnegative_integer, default=123,
                        help="ice-slip RNG seed (default: 123)")
    parser.add_argument("--action-seed", type=nonnegative_integer, default=456,
                        help="separate random-policy seed (default: 456)")
    parser.add_argument("--render-mode", choices=("none", "ansi", "human"), default="none",
                        help="ansi prints final grids; human prints every reset/step")
    parser.add_argument("--policy", choices=tuple(CLI_POLICIES), default="value_iteration",
                        help="saved policy to play; random is an explicit baseline")
    args = parser.parse_args(argv)
    try:
        policy = load_policy(CLI_POLICIES[args.policy])
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))
    mode = None if args.render_mode == "none" else args.render_mode
    print(f"{CLI_POLICIES[args.policy]} | seed={args.seed} action_seed={args.action_seed} | gamma=0.99")
    with gym.make("IcyGridWorld-v0", render_mode=mode) as env:
        env.action_space.seed(args.action_seed)
        for episode in range(1, args.episodes + 1):
            observation, _ = env.reset(seed=args.seed if episode == 1 else None)
            total_reward = 0.0
            while True:
                observation, reward, terminated, truncated, info = env.step(requested_action(policy, observation, env.action_space))
                total_reward += reward
                if terminated or truncated:
                    break
            print(f"Episode {episode}: steps={info['steps']} total_reward={total_reward:.1f} "
                  f"observation={observation} position={info['position']} "
                  f"terminated={terminated} truncated={truncated}")
            if mode == "ansi":
                print(env.render())


if __name__ == "__main__":
    main()
