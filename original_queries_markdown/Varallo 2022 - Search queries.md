+-------+------------------------------------------------------+------+
| Table |                                                      |      |
| S1.   |                                                      |      |
| S     |                                                      |      |
| earch |                                                      |      |
| str   |                                                      |      |
| ategy |                                                      |      |
| emp   |                                                      |      |
| loyed |                                                      |      |
| d     |                                                      |      |
| uring |                                                      |      |
| the   |                                                      |      |
| syste |                                                      |      |
| matic |                                                      |      |
| r     |                                                      |      |
| eview |                                                      |      |
+-------+------------------------------------------------------+------+
| Dat   | Search string                                        | Res  |
| abase |                                                      | ults |
+-------+------------------------------------------------------+------+
| P     | [#1: surger\* OR operative\* OR surgical OR          | 4863 |
| ubmed | postsurgical OR postoperative OR post-surgical OR    |      |
|       | post-operative OR \"Surgical Procedures,             |      |
|       | Operative\"\[Mesh\]]{.mark}                          |      |
|       |                                                      |      |
|       | [#2: sleep OR sleep apnea OR OSA OR insomnia OR      |      |
|       | hypersomnia OR narcolepsy OR sleep quality OR sleep  |      |
|       | quantity OR sleep duration OR \"circadian rhythm\"   |      |
|       | OR \"Sleep Wake Disorders\"\[MeSH\] OR \"Sleep       |      |
|       | Disorders, Circadian Rhythm\"\[Mesh\]]{.mark}        |      |
|       |                                                      |      |
|       | [#3: pain OR \"NRS\" OR \"VAS\" OR \"numeric rating  |      |
|       | scale\" OR \"visual analogue scale\"]{.mark}         |      |
|       |                                                      |      |
|       | #4: #1 AND #2 AND #3                                 |      |
+-------+------------------------------------------------------+------+
| S     | [(TITLE-ABS-KEY (pain OR \"numeric rating scale\"    | 891  |
| copus | OR \"Visual analogue scale\" OR \"NRS\" OR \"VAS\"   |      |
|       | ) )  AND  ( TITLE-ABS-KEY ( sleep  OR  sleep         |      |
|       | AND apnea  OR  osa  OR  insomnia  OR  hypersomnia    |      |
|       | OR  narcolepsy  OR  sleep  AND quality  OR  sleep    |      |
|       | AND quantity  OR  sleep  AND duration  OR            |      |
|       | \"circadian rhythm\"  OR  \"Sleep Wake               |      |
|       | Disorders\" ) )  AND  ( TITLE-ABS-KEY ( surger\*     |      |
|       | OR  operative\*  OR  surgical  OR  postsurgical  OR  |      |
|       | postoperative  OR  \"post-surgical\"  OR             |      |
|       | \"post-operative\" ) ) ]{.mark}                      |      |
+-------+------------------------------------------------------+------+
| E     | [#1: \'pain\'/exp OR pain]{.mark}                    | 1082 |
| MBASE |                                                      |      |
|       | [#2: \'sleep disorder\'/exp OR sleep OR apnea OR osa |      |
|       | OR insomnia OR hypersomnia OR narcolepsy OR (sleep   |      |
|       | AND quality) OR (sleep AND quantity) OR (sleep AND   |      |
|       | duration)]{.mark}                                    |      |
|       |                                                      |      |
|       | [#3: postsurgical OR postoperative OR \'post         |      |
|       | surgical\' OR \'post operative\' OR \'postoperative  |      |
|       | pain\'/exp]{.mark}                                   |      |
|       |                                                      |      |
|       | [#4: \'risk factor\'/exp OR longitudinal OR          |      |
|       | predictor\* OR correlati\* OR regressi\* OR          |      |
|       | \'predictor variable\' OR determinant]{.mark}        |      |
|       |                                                      |      |
|       | #5: #1 AND #2 AND #3 AND #4                          |      |
+-------+------------------------------------------------------+------+
| Web   | [ALL=(pain OR \"NRS\" OR \"VAS\" OR \"numeric rating | 810  |
| of    | scale\" OR \"visual analogue scale\") AND            |      |
| Sc    | ALL=(surger\* OR operative\* OR surgical OR          |      |
| ience | postsurgical OR postoperative OR post-surgical OR    |      |
|       | post-operative) AND ALL=(sleep OR sleep apnea OR OSA |      |
|       | OR insomnia OR hypersomnia OR narcolepsy OR sleep    |      |
|       | quality OR sleep quantity OR sleep duration OR       |      |
|       | \"circadian rhythm\") AND ALL=(\"risk factor\*\" OR  |      |
|       | longitudinal OR predictor\* OR correlati\* OR        |      |
|       | regressi\* OR \'predictor variable\' OR              |      |
|       | determinant)]{.mark}                                 |      |
+-------+------------------------------------------------------+------+
