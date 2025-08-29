---
title: 'HierarchyCraft: A Benchmark Builder for Hierarchical Reasoning'
tags:
  - Python
  - Hierarchy
  - Hierarchical
  - Reasoning
  - Reinforcement
  - Learning
  - Planning
  - Planification
  - Program
  - Synthesis
authors:
  - name: Mathis Fédérico
    orcid: 0009-0002-2624-3417
    affiliation: "1, 2"
  - name: Shang Wang
    orcid: 0009-0000-0130-0468
    affiliation: "1"
  - name: Yuxuan Li
    orcid: 0000-0001-5522-312X
    affiliation: "1, 3"
  - name: Matthew E. Taylor
    orcid: 0000-0001-8946-0211
    affiliation: "1, 3"
affiliations:
 - name: Department of Computing Science, University of Alberta, Canada
   index: 1
 - name: CentraleSupelec, University of Paris-Saclay, France
   index: 2
 - name: Alberta Machine Intelligence Institute (Amii), Canada
   index: 3
date: 06 May 2024
bibliography: paper.bib

---


# Summary

Hierarchical reasoning poses a fundamental challenge in the field of artificial intelligence [@10.1098/rstb.2013.0480]. Existing methods may struggle when confronted with hierarchical tasks [@bacon2017option;@heess2016learning; @nachum2018data], yet despite the importance of understanding how the structure of an underlying hierarchy affects task difficulty, there is a lack of suitable environments or benchmarks to facilitate this exploration.

We introduce **[HierarchyCraft](https://github.com/IRLL/HierarchyCraft)**, a software package that allows researchers to create custom environments based on their hierarchical structures, enabling the study of hierarchical reasoning.

To isolate hierarchical behavior and ensure compatiblilty with classical planning algorithms, we exclude unstructured data like images and text, avoiding the complexity of feature extraction, and allowing comparisons between classical planning and reinforcement learning.

HierarchyCraft simplifies the creation of diverse hierarchical environments from a list of [a single building block](https://irll.github.io/HierarchyCraft/hcraft/transformation) as showcased by the [set of pre-defined environments](https://irll.github.io/HierarchyCraft/hcraft/examples).


![HierarchyCraft is at the intersection of reinforcement learning, planning, hierarchical reasoning and program synthesis.\label{fig:HierachyCraft_domain_position}](docs/images/HierachyCraft_domain_position.png){ width=70% }


# Statement of need

HierarchyCraft is designed as a user-friendly Python library for constructing environments tailored to the study of hierarchical reasoning in the contexts of reinforcement learning, classical planning, and program synthesis as displayed in \autoref{fig:HierachyCraft_domain_position}.

Analysis and quantification of the impacts of diverse hierarchical structures on learning agents is essential for advancing hierarchical reasoning.
However, current hierarchical benchmarks often limit themselves to a single hierarchical structure per benchmark, and present challenges not only due to this inherent hierarchical structure but also because of the necessary representation learning to interpret the inputs.

HierarchyCraft is a benchmark builder (not a benchmark) designed to study how different hierarchical structures impact the performance of classical planners and reinforcement learning algorithms. It includes several [examples](https://github.com/IRLL/HierarchyCraft/tree/master/src/hcraft/examples), detailed in the [documentation](https://irll.github.io/HierarchyCraft/hcraft/examples), that can serve as initial benchmarks. These examples include basic parametrised hierarchical structures (Random, Recursive, Tower) and fixed structures imitating other environments (MineHCraft for Minecraft tasks, MiniHCraft for Minigrid tasks). Researchers are encouraged to create custom hierarchical environments to explore structures of their choice.

We argue that arbitrary hierarchical complexity can emerge from simple rules.
To the best of our knowledge, no general frameworks currently exist for constructing environments dedicated to studying the hierarchical structure itself. We next highlight five related benchmarks, underscoring the necessity for the development of a tool like HierarchyCraft.


### GridWorld

GridWorld, a general class of 2D grid-based environments, is frequently utilised in hierarchical reinforcement learning research, notably within the options framework [@10.1016/s0004-3702(99)00052-1].

![Example of Minigrid environments hierarchical structures and their relationships. There are only a few possible subtasks and most of them are navigation tasks (in green).\label{fig:MinigridHierarchies}](docs/images/MinigridHierarchies.png){ width=100% }


Minigrid [@MinigridMiniworld23] is a user-friendly Python library that not only implements a GridWorld engine but also expands its capabilities. This allows researchers to create more intricate scenarios by introducing additional rooms, objectives, or obstacles.

As illustrated in \autoref{fig:MinigridHierarchies}, GridWorld environments only exhibit **limited and similar hierarchical structures** that primarily focus on navigation tasks, making these hierarchies mostly sequential.

### Minecraft

A good example of a hierarchical task is the collection of diamonds in the popular video game Minecraft, as showcased in the MineRL competition [@guss2021minerl2020], where hierarchical reinforcement learning agents have dominated the leaderboard[@milani2020minerl2019].

Due to sparse rewards, the difficulty of exploration, and long time horizons in this procedurally generated sandbox environment, DreamerV3 [@dreamerv3] recently became the first algorithm to successfully collect diamonds in Minecraft without prior training or knowledge.
Unfortunately, DreamerV3 required training on an Nvidia V100 GPU for 17 days, gathering roughly 100 million environmental steps. Such **substantial computational resources are unavailable to many researchers**, impeding the overall progress of research on hierarchical reasoning.

Moreover, although Minecraft has an [undeniably complex hierarchical structure](https://irll.github.io/HierarchyCraft/hcraft/examples/minecraft.html), **this underlying hierarchical structure is fixed** and cannot be modified without modding the game, a complex task for researchers.


### Crafter

Crafter [@hafner2022benchmarking] presents a lightweight grid-based 2D environment, with game mechanics akin to Minecraft and poses similar challenges (exploration, representation learning, rewards sparsity and long-term reasoning) at much lower compute cost.

![Hierarchical structure of the Crafter environment as presented by the authors of Crafting with their success rates. Inspired by Figure 4 of [@hafner2022benchmarking].\label{fig:CrafterGraph}](docs/images/CrafterRequirementsGraph.png){ width=80% }


Although Crafter offers 22 different tasks displayed in \autoref{fig:CrafterGraph}, the **underlying hierarchical structure is fixed**, restricting how researchers can investigate the impacts of changes to the hierarchical structure.

Moreover, the tasks considered by the authors do not encompass various navigation-related subtasks (such as finding water, locating a cow, waiting for a plant to grow, or returning to a table), nor do they include certain optional but beneficial subtasks (for example, using swords or the skill of dodging arrows can make the task of defeating skeletons easier).

These omissions results in abrupt drops in success rates within the hierarchy, rather than a more gradual progression in difficulty. This highlights that the hierarchy presented by the authors is incomplete, as it fails to capture the full range of subtasks in Crafter and the necessary or helpful interactions between them for successfully completing higher-level tasks.


### Arcade Learning Environment (Atari)
The arcade learning environment [@10.5555/2832747.2832830] stands as a standard benchmark in reinforcement learning, encompassing over 55 Atari games. However, **only a few of these games, such as Montezuma’s Revenge and Pitfall, necessitate hierarchical reasoning**.

Each Atari game has a **fixed hierarchy that cannot be modified** and agents **demand substantial computational resources** to extract relevant features from pixels or memory, significantly slowing down experiments.

<!--
### NetHack Learning Environment

The NetHack learning environment [@kuttler2020nethack] is an extremely hierarchical environment based on the game NetHack, where the observation is a grid composed of hundreds of possible symbols.

In fact, NetHack is **too complex for agents to learn**, it requires many environment steps for agents to acquire domain-specific knowledge. 10B steps were required for the NeurIPS 2021 NetHack challenge [@2021NetHack], making it impractically long for a benchmark. Moreover, the NetHack game also has a **fixed underlying hierarchy** that cannot be easily modified. -->


### PDDLGym

PDDLGym [@PDDLgym] is a Python library that automatically constructs Gym environments from Planning Domain Definition Language (PDDL) domains and problems. PDDL [@PDDL] functions as a problem specification language, facilitating the comparison of different symbolic planners.

However, constructing PDDL domains and problems with a hierarchical structure is challenging and time-consuming, especially for researchers unfamiliar with PDDL-like languages.

Additionally, PDDLGym is **compatible only with PDDL1** and does not support numeric-fluents introduced in PDDL 2.1 that are required to represent quantities in the inventories of HierarchyCraft environments.


### Abstraction and Reasoning Corpus (ARC)


The Abstraction and Reasoning Corpus (ARC) [@Chollet2019OnTM], is both hierarchical and diverse, as each task exhibits its own implicit hierarchical structure. However, these hierarchical structures are not explicitly provided within the dataset, such as with shorter programs for each task. Making these hierarchical structures explicit would also contribute significantly to the development of hierarchical reasoning like what HierarchyCraft is trying to achieve.

Much like Gridworld, ARC tasks require feature extraction from 2D grids, leveraging priors related to their spatial nature, which bias the nature of the tasks on that specific data structure.

Additionaly ARC tasks do not emphasise long-term reasoning as they are relatively short compared to tasks within other benchmarks like Minecraft or even Gridworld; this makes underlying hierarchical structures shallow for each task and more wide that deep for the whole corpus.

Partitioning those underlying hierarchical structures and classifying them relatively to the difficulty of finding a solution, independently of the solution's nature, is at the core of HierarchyCraft's motivation.


## Design goals

HierarchyCraft aims to be a fruitful tool for investigating hierarchical reasoning, focussing on achieving the following four design goals.


### 1. Hierarchical by design

The action space of HierarchyCraft environments consists of subtasks, referred to as *[Transformations](https://irll.github.io/HierarchyCraft/hcraft/transformation.html)*, as opposed to detailed movements and controls. But each *Transformations* has specific requirements to be valid (e.g. have enough of an item, be in the right place), and these requirements may necessitate the execution of other *Transformations* first, inherently creating a hierarchical structure in HierarchyCraft environments.
This concept  is visually represented by the *Requirements Graph* depicting the hierarchical relationships within each HierarchyCraft environment.
The *Requirements Graph* is directly constructed from the list of *Transformations* composing the environement, as illustrated in \autoref{fig:TransformationToRequirements}.
Requirements Graphs should be viewed as a generalisation of previously observed graphical representations from related works, including \autoref{fig:CrafterGraph} and \autoref{fig:MinigridHierarchies}.

![How subtasks build a hierarchical structure.\label{fig:TransformationToRequirements}](docs/images/TransformationToRequirementsLarge.png){ width=75% }


### 2. Easy to use and customise

HierarchyCraft is a versatile framework enabling the creation of diverse hierarchical environments.
The library is designed to be simple and flexible, allowing researchers to define their own hierarchical environments with detailed guidance provided in the documentation.
To showcase the range of environments possible within HierarchyCraft, multiple examples are provided.


### 3. No feature extraction needed
In contrast to benchmarks that yield grids, pixel arrays, text, or sound, HierarchyCraft directly provides a low-dimensional representation that does not require further features extraction, as depicted in \autoref{fig:HcraftState}.

![HierarchyCraft compact state representation.\label{fig:HcraftState}](docs/images/HierarchyCraftStateLarge.png){ width=80% }

This not only saves computational time but also enables researchers to concentrate on hierarchical reasoning, allows the use of classical planning frameworks such as PDDL [@PDDL] or ANML [@ANML], and enables the creation of any arbitrary complex custom environment from a list of *Transformations*, nothing more.

### 4. Compatible with multiple frameworks

HierarchyCraft environments are directly compatible with both reinforcement learning through Gymnasium [@gymnasium] and planning through the Unified Planning Framework [@UPF] (see \autoref{fig:HierarchyCraft-pipeline}).
This compatibility facilitates usage by both the reinforcement learning and planning communities.

![HierarchyCraft pipeline into different representations.\label{fig:HierarchyCraft-pipeline}](docs/images/HierarchyCraft_pipeline.png){ width=80% }


# Acknowledgements

This work was made possible by the research program of the engineering cursus at CentraleSupelec, University of Paris-Saclay, France.

The research was conducted at the Intelligent Robot Learning (IRL) Lab, University of Alberta, which is supported in part by research grants from the Alberta Machine Intelligence Institute (Amii); a Canada CIFAR AI Chair, Amii; Compute Canada; Huawei; Mitacs; and NSERC.

Special thanks to Laura Petrich and other members of the IRL Lab for their assistance in finding and describing related works, their critical thinking on the project, and their contributions to the revisions of the documentation and report.


# References
