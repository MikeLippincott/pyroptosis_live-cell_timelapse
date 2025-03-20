suppressWarnings(suppressPackageStartupMessages(library(ggplot2)))
suppressWarnings(suppressPackageStartupMessages(library(cowplot)))
suppressWarnings(suppressPackageStartupMessages(library(dplyr)))
suppressWarnings(suppressPackageStartupMessages(library(arrow)))
suppressWarnings(suppressPackageStartupMessages(library(argparse)))

percent_cell_mAP_file_path <- file.path("../results/mAP_cell_percentages.parquet")
across_channels_mAP_file_path <- file.path("../results/mAP_across_channels.parquet")

percent_cell_mAP <- arrow::read_parquet(percent_cell_mAP_file_path)
across_channels_mAP <- arrow::read_parquet(across_channels_mAP_file_path)
dim(percent_cell_mAP)
dim(across_channels_mAP)

head(percent_cell_mAP)

# get the average mAP for each treatment and timepoint
percent_cell_mAP <- percent_cell_mAP %>%
  group_by(Metadata_treatment, Metadata_Time, shuffle, percentage_of_cells) %>%
  summarise(mAP = mean(mean_average_precision))

head(percent_cell_mAP)

width <- 15
height <- 15
options(repr.plot.width = width, repr.plot.height = height)
percent_cell_plot <- (
    ggplot(data = percent_cell_mAP, aes(x = Metadata_Time, y = mAP))
    + geom_line(aes(group = Metadata_treatment, color = Metadata_treatment))
    + facet_grid(shuffle ~ percentage_of_cells)
)
percent_cell_plot


