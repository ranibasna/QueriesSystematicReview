╭─────────────────────────────────────────────────────╮
│  > Ok I have created the new branch. What are the   │
│    changes that need to be done. Explian to me      │
│    before doing any changes                         │
╰─────────────────────────────────────────────────────╯

✦ Excellent! Now that you're on a new branch, we can
  safely implement the changes to support multiple
  studies. Here is a detailed plan of the changes I
  will make. Please review it, and once you approve, I
  will proceed with the implementation.

  Plan for Multi-Study Support

  The goal is to isolate each study's files and
  results. We will achieve this by creating a new
  directory structure and then updating the
  run_workflow.sh script to work with it.

  Step 1: Restructure the Project Directory

  I will create a new top-level directory called
  studies. Each subdirectory within studies will
  represent a single, self-contained systematic review
   study.

   1. Create `studies` directory: I will start by
      creating a new directory named studies in the
      root of your project.

   2. Create a directory for your first study: I will
      create a directory inside studies for your
      current study. Based on the context, a good name
       would be MS_and_Sleep.

   3. Move study-specific files: I will move all the
      files and directories that are specific to your
      "MS and Sleep" study into the new
      studies/MS_and_Sleep directory. This will
      include:
       * Queries/
       * sealed_outputs/
       * benchmark_outputs/
       * aggregates/
       * aggregates_eval/
       * Gold_list__all_included_studies_.csv
       * concept_terms_MS_sleep_RCT.csv
       * sr_config.toml
       * .env
       * The .gemini/ directory and its contents.

  After this restructuring, the
  llm_sr_select_and_score.py script and the
  run_workflow.sh script will remain at the top level,
   as they are the tools that will operate on the
  different studies.

  Step 2: Update the `run_workflow.sh` Script

  The run_workflow.sh script needs to be made aware of
   the new directory structure.

   1. Add a `--study-dir` argument: I will add a new,
      required command-line argument to the script
      called --study-dir. This will allow you to
      specify which study you want to run the workflow
       on.

   2. Update file paths: I will modify the script to
      use the --study-dir argument to construct the
      correct paths to all the input files and output
      directories. For example, instead of using a
      hardcoded path like Queries/queries.txt, the
      script will use
      "$STUDY_DIR/Queries/queries.txt".

  How You Will Use the New Workflow

  After these changes, you will run the workflow for a
   specific study like this:

   1 ./run_workflow.sh --study-dir
     "studies/MS_and_Sleep" --query-gen
     "/run_sleep_ms"

  This command tells the script to run the entire
  workflow on the files located within the
  studies/MS_and_Sleep directory. This ensures that
  the results for your "MS and Sleep" study are kept
  completely separate from any other studies you might
   add in the future.

  ---

  Please review this plan. If you are happy with it, I
   will proceed with making the necessary changes to
  the file system and the run_workflow.sh script.