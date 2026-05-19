import sys
import numpy as np
import pandas as pd
from scipy.stats import sem
import matplotlib.pyplot as plt


def plot(data, group_var):
    """
    data: dataframe with data to plot
    group_var: variable to group data by (x.g., ACxRA combination)
    """

    ## MAPPING PARTICIPANT RATINGS BY ACxRA and CONFIDENCE IN RESPONSE
    ## Grouping by ACxRA combination assigned to question
    grouped = data.groupby(group_var)

    ## Computing means and standard errors for participant's ratings for Alex and AP-5 and confidence 
    means = grouped[['Alex_rating', 'AP5_rating', 'confidence']].mean()
    errors = grouped[['Alex_rating', 'AP5_rating', 'confidence']].agg(sem)

    ## 95% confidence intervals
    ci_95 = errors * 1.96

    conditions = means.index

    fig, ax = plt.subplots(3, 1, figsize=(10, 15))

    if group_var == 'acra_assigned':
        plot_name = 'ACxRA combination'
    else:
        plot_name = group_var

    for i, column in enumerate(['Alex_rating', 'AP5_rating', 'confidence']):
        ax[i].errorbar(conditions, means[column], yerr=errors[column], fmt='o', capsize=5, label='SEM', color='blue')
        ax[i].errorbar(conditions, means[column], yerr=ci_95[column], fmt='o', capsize=5, label='95% CI', color='red', alpha=0.5)
        ax[i].set_title(f'Mean, SEM, and 95% CI of {column} by ' + plot_name)
        ax[i].set_xlabel(plot_name)
        ax[i].set_ylabel(f'Mean {column}')
        
    # Legend
    handles, labels = ax[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    plt.tight_layout()
    plt.savefig('plots/' + str(sys.argv[2]) + '_mean_and_sem_95ci_by_' + plot_name + '.png',
        facecolor="white",
        transparent=True,)



def main():
    if len(sys.argv) != 3:
        sys.exit("Please pass path to data file and name of experiment as arguments.")

    data = pd.read_csv(sys.argv[1])

    data["duration_mins"] = data["Duration (in seconds)"].astype(float) / 60.0

    ## Histogram for duration
    plt.figure(figsize=(8, 6))
    bins = list(range(0, 55, 5))
    data["duration_mins"].plot(kind="hist", bins=bins)
    plt.xlabel("Duration (minutes)", fontsize=14)
    plt.ylabel("Frequency (number of respondents)", fontsize=14)
    plt.title("Time taken to complete survey", fontsize=16)
    # Add grid lines
    plt.grid(True, linestyle="--", alpha=0.5)
    # Set x-axis tick marks for each 5-minute increment
    plt.xticks(range(0, 51, 5))
    # Save the plot to a file
    plt.savefig(
        "plots/" + str(sys.argv[2]) + "_duration_histogram.png",
        facecolor="white",
        transparent=True,
    )

    ## Mapping responsibility to float
    rating_map = {"Low Responsibility": 0.0, "Medium Responsibility": 0.5, "High Responsibility": 1.0}
    cf_rating_map = {"Low confidence": 0.0, "Medium confidence": 0.5, "High confidence": 1.0}
    data['Alex_rating'] = data['Alex_rating'].map(rating_map)
    data['AP5_rating'] = data['AP5_rating'].map(rating_map)
    data['confidence'] = data['confidence'].map(cf_rating_map)

    vars = ["acra_assigned", "bias", "info", "num-CF-agent"]

    for var in vars:

        if var == "acra_assigned":
            data_filtered = data[data['acra_assigned'].str.strip() != '']
            plot(data_filtered, var)
        elif var == "num-CF-agent":
            # Column 'CF' contains number of counterfactuals, 'agent-CF' contains which Agent's CF was shown
            # Combining into one for plotting
            data["num-CF-agent"] = data["CF"] + "-Agent-" + data["agent-CF"]
            data["num-CF-agent"] = data["num-CF-agent"].fillna("factual")
            plot(data, var)
        else:
            plot(data, var)



if __name__ == '__main__':
    main()