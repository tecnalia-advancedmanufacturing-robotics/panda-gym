# nextage-gym

Set of robotic environments based on PyBullet physics engine and gymnasium.

[![PyPI version](https://img.shields.io/pypi/v/nextage-gym.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/nextage-gym/)
[![Downloads](https://static.pepy.tech/badge/nextage-gym)](https://pepy.tech/project/nextage-gym)
[![GitHub](https://img.shields.io/github/license/qgallouedec/nextage-gym.svg)](LICENSE.txt)
[![build](https://github.com/qgallouedec/nextage-gym/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/qgallouedec/nextage-gym/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/qgallouedec/nextage-gym/branch/master/graph/badge.svg?token=pv0VdsXByP)](https://codecov.io/gh/qgallouedec/nextage-gym)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![arXiv](https://img.shields.io/badge/cs.LG-arXiv%3A2106.13687-B31B1B.svg)](https://arxiv.org/abs/2106.13687)

## Documentation

Check out the [documentation](https://nextage-gym.readthedocs.io/en/latest/).

## Installation

### Using PyPI

```bash
pip install nextage-gym
```

### From source

```bash
git clone https://github.com/qgallouedec/nextage-gym.git
pip install -e nextage-gym
```

## Usage

```python
import gymnasium as gym
import nextage_gym

env = gym.make('PandaReach-v3', render_mode="human")

observation, info = env.reset()

for _ in range(1000):
    action = env.action_space.sample() # random action
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()

env.close()
```

You can also [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/qgallouedec/nextage-gym/blob/master/examples/PickAndPlace.ipynb)

## Baselines results

Baselines results are available in [rl-baselines3-zoo](https://github.com/DLR-RM/rl-baselines3-zoo) and the pre-trained agents in the [Hugging Face Hub](https://huggingface.co/sb3).

Environments are widely inspired from [OpenAI Fetch environments](https://openai.com/blog/ingredients-for-robotics-research/).
