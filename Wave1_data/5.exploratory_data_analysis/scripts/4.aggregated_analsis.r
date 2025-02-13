library(ggplot2)

agg_file_path <- file.path("../../4.processing_profiled_features/data/aggregated/live_cell_pyroptosis_wave1_first_time_norm_fs_agg.parquet")

agg_df <- arrow::read_parquet(agg_file_path)
agg_df$unique_group <- paste(agg_df$Metadata_Well, agg_df$Metadata_FOV, sep="_")
head(agg_df)

width <- 15
height <- 5
options(repr.plot.width=width, repr.plot.height=height)
# plot the timelapse _profiles for a given feature
timelapse_plot <- (
    # group the timepoints by the feature
    ggplot(agg_df, aes(x=Metadata_Time, y=Nuclei_Texture_InfoMeas2_BF_3_03_256), fill=Metadata_Well)
    + geom_line(aes(group=unique_group, color=Metadata_Well), alpha=0.5)
    + theme_bw()
    + theme(legend.position = "none")
    # + facet_wrap(~unique_group)
)
timelapse_plot
