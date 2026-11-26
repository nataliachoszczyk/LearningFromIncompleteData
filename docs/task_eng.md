# MED project task (English)

This file is a translation of `docs/task.md`. The Polish text is the original.

Course page: https://leon.pw.edu.pl/course/view.php?id=2333

## Topic

**Inference from incomplete data and partial knowledge.** Implement one method for classification or inference when the data has missing values. Examples: rough sets, decision rules for incomplete data, or a comparison with imputation methods.

Specific goals:

- Measure the robustness of the algorithm at different levels of missing values.
- Compare the quality of inference for different strategies to handle missing values.

Our project combines two variants:

- **7.1. Rough sets for incomplete data:** Kryszkiewicz, M. (1998). Rough set approach to incomplete information systems. *Information Sciences*, 112(1–4), 39–49.
- **7.3. kNN imputation:** Troyanskaya, O., Cantor, M., Sherlock, G., Brown, P., Hastie, T., Tibshirani, R., Botstein, D., Altman, R. B. (2001). Missing value estimation methods for DNA microarrays. *Bioinformatics*, 17(6), 520–525.

## Goal of the project

Examine the properties of our own implementation of the algorithm:

- the run time for different values of the input parameters,
- the effect of the parameter values on the results,
- the scalability for the size of the data (the number of records and the number of attributes),
- the specific goals of the topic (above).

Do the tests on more than one dataset.

## Environment

We select the programming language, the tools and the libraries. The use of the tools must be legal for student projects. Popular programming languages are preferred.

## Team size

The task is for one person. A team of two is possible, but the team must agree the scope with the teacher.

## Dates

**2026-11-26: selection of the topic.** Send three preferred topics by e-mail, in order of preference. Put "[projekt MED]" in the subject.

**2026-12-17: part 1, the design of the implementation.** The design is not the implementation. It must show:

- the structure of the implementation (functions, classes), with a reference to each step of the algorithm,
- the data structures for the source data,
- the data structures of the algorithm,
- an estimate of the efficiency of the solution.

Part 1 is a personal presentation at a project consultation. It has:

- a presentation (for example .ppt) of the scope, the technologies and the test plan,
- a discussion of the design document.

Agree the date with the teacher. Upload the design document before the presentation.

**2027-01-21: part 2, the complete project.** It is a meeting at a project consultation. It has:

- a presentation (for example .ppt) of the main parts of the project,
- a demonstration of the software,
- a discussion of the tests, the results and the conclusions.

Agree the date with the teacher. Upload the documentation before the meeting.

## Points

- Part 1: 15 points.
- Part 2: 30 points.
- Total: 45 points. The percentage of the points gives the final grade.

## Documentation

The final documentation has these chapters:

1. Introduction and definition of the problem
2. Description of the algorithm, with references to the literature
3. Description of the implementation
4. User guide (how to run and use the implementation)
5. Description of the datasets
6. Results of the experiments that show the properties of the solution
7. Conclusions
8. Bibliography
9. Source code in separate files

Use public datasets for the experiments, for example:

- https://archive.ics.uci.edu/datasets
- http://fimi.uantwerpen.be/data/
- https://github.com/deric/clustering-benchmark
- http://www.philippe-fournier-viger.com/spmf/index.php?link=datasets.php

Upload the documentation of the two parts to https://leon.pw.edu.pl/course/view.php?id=2333 before the dates above.
