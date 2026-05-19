# Cleaned data from Prolific Surveys

## Data Formats Description
Contains pre-pilot and pilot survey responses in the following formats:

1. Data files containing relevant columns from Qualtrics in the long format, i.e., there is only 1 row per ACxRA question per participant.
- Thus, 250 rows of participant responses for the pilot study (5 rows for each participant, 1 for each ACxRA question they answered.)
- Files in this format:
    * Pre-pilot study: 2025_pre_pilot_data_long_format.csv
    * Pilot study: 2025_pilot_data_with_responsibilities_long_format.csv
- For computing agreement of a participant's ratings for Alex and AP-5 with the ratings by a particular ACxRA combination, the formula used is: 0.5 * ( Indicator( r_Alex(calculated for combo) == r_Alex(reported by participant) + r_AP5(calculated for combo) == r_AP5(reported by participant) ) )
- Contains the following columns:
    * "ResponseId": Prolific identifier for a participant's record for a survey. 
    * "Duration (in seconds)": Time taken by participant to finish the survey in seconds. 
    * "PROLIFIC_PID": Prolific identifier for a participant.
    * "num_counterfactuals": number of counterfactuals the participant saw. 
    * "info": amount of information treatment for the participant (i.e., whether agents could see each others' cards or not). 
    * "CF": whether the participant got factual/1 counterfactual/2 counterfactual treatment.
    * "bias": biased hand treatment the participant was shown (biased against Agent 0, 1, or no bias).
    * "agent-CF": if the participants were shown a counterfactual, then which counterfactual (i.e., counterfactual for Agent 0, 1, or both).
    * "acra_assigned": the ACxRA combination assigned for that question. 
    * "acra_display_order": display order of ACxRA questions in treatments with counterfactuals 
    * "factual_only_traj_display_order": display order of ACxRA questions in factual-only treatments
    * "traj_number": Qualtrics question id of the trajectory shown in the ACxRA question
    * "Alex_rating": Participant's responsibility rating for Alex for that question. 
    * "AP5_rating": Participant's responsibility rating for AP-5 for that question. 
    * "confidence": Participant's confidence rating for how confident they are in their responses for that question.
    * "BFxCH_Alex_rating_traj": Responsibility assignment for Alex for this trajectory for BFxCH combination for the bias shown to participant. 
    * "BFxCH_AP5_rating_traj": Responsibility assignment for AP5 for this trajectory for BFxCH combination for the bias shown to participant. 
    * "BFxCH_agreement": Agreement between participant's ratings and computed ratings for BFxCH.
    * "HPxCH_Alex_rating_traj": Responsibility assignment for Alex for this trajectory for HPxCH combination for the bias shown to participant. 
    * "HPxCH_AP5_rating_traj": Responsibility assignment for AP5 for this trajectory for HPxCH combination for the bias shown to participant. 
    * "HPxCH_agreement": Agreement between participant's ratings and computed ratings for HPxCH.
    * "HPxTR_Alex_rating_traj": Responsibility assignment for Alex for this trajectory for HPxTR combination for the bias shown to participant. 
    * "HPxTR_AP5_rating_traj": Responsibility assignment for AP5 for this trajectory for HPxTR combination for the bias shown to participant. 
    * "HPxTR_agreement": Agreement between participant's ratings and computed ratings for HPxTR.
    * "TRxCH_Alex_rating_traj": Responsibility assignment for Alex for this trajectory for TRxCH combination for the bias shown to participant. 
    * "TRxCH_AP5_rating_traj": Responsibility assignment for AP5 for this trajectory for TRxCH combination for the bias shown to participant. 
    * "TRxCH_agreement": Agreement between participant's ratings and computed ratings for TRxCH.
    * "TRxTR_Alex_rating_traj": Responsibility assignment for Alex for this trajectory for TRxTR combination for the bias shown to participant. 
    * "TRxTR_AP5_rating_traj": Responsibility assignment for AP5 for this trajectory for TRxTR combination for the bias shown to participant. 
    * "TRxTR_agreement": Agreement between participant's ratings and computed ratings for TRxTR.
    * "trajectory": trajectory (trajectory number only, in int)





## Selection of trajectories
Trajectories for each treatment were selected randomly, including for factual-only settings. 
- So for combinations with counterfactuals, 5 random trajectory numbers were selected for each of the following combinations: number of counterfactuals = [factual-cf-agent0, factual-cf-agent1, factual-cf-both-agents] x bias = ["biased_none", "biased_0", "biased_1"] x info = ["partial", "full"] x acra = ["BFxCH", "HPxCH", "HPxTR", "TRxCH", "TRxTR"].
   * For example, for the combination with number of counterfactuals = factual-cf-agent0, info = partial, and bias = biased_none, and acra = BFxCH, the following 5 trajectories were selected: [289 153 598 697 43]. Any participant assigned to this treatment would be randomly shown 1 of these 5 trajectories.
- For combinations with factuals-only scenarios, 25 random trajectory numbers were selected for each of the following combinations: number of counterfactuals = [factuals-only] x bias = ["biased_none", "biased_0", "biased_1"] x info = ["partial", "full"].
   * For example, for the combination with factuals-only setting, info = partial, and bias = biased_none, the following 25 trajectories were selected: [32 854 527 70 474 326 850 872 129 521 390 244 510 378 498 837 473 848 637 35 164 442 159 687 241]. Any participant assigned to this treatment would be randomly shown 5 of these 25 trajectories.
     
- In case of a trajectory with game that ended in a draw, a new random number was generated as the replacement trajectory (since we decided not to have games that end in draws to avoid confusing participants). "../qualtrics-survey/record-questions-final.csv" contains the seed number for the random number generator used to generate random numbers as well as the list of selected trajectories. 


## Data cleaning script 
data_desired_format.py cleans the data. 
- It takes the following arguments: 
    * the path to a sparse CSV file of survey data as the first argument. 
    * name of the survey (e.g., "pre-pilot" or "pilot") as the second argument.
- It cleans the data and creates 2 new files under a "cleaned_data" subdirectory:
    * survey_name (second argument) + "_condensed_data_all_wide_format.csv": file with all survey data in condensed form in wide format (#1 in Data Formats Description).
    * survey_name (second argument) + "_condensed_data_with_responsibilities_long_format.csv": file with a subset of columns in long format (#2 in Data Formats Description)


## Script to create plots
- plots.py plots the histogram of duration taken by participants to complete survey. It also plots the mean participant rating and mean confidence rating along with their standard error and 95% confidence intervals for:
   * mean participant ratings and confidence for each ACxRA combination (BFxCH, HPxCH, HPxTR, TRxCH, TRxTR) for Alex and AP-5
   * mean participant ratings and confidence for each bias treatment (bias against Agent 0, bias agaist Agent 1, no bias) for Alex and AP-5
   * mean participant ratings and confidence for each amount-of-information treatment (full information, partial information) for Alex and AP-5
   * mean participant ratings and confidence for each number of counterfactuals treatment (factual-only, counterfactual for Agent 0, counterfactual for Agent 1, both counterfactuals) for Alex and AP-5
- It takes the following arguments: 
    * the path to a CSV file of survey data in the LONG format (data format #2 above) as the first argument. 
    * name of the survey (e.g., "pre-pilot" or "pilot") as the second argument. (used for naming stored plots)
