library(ggplot2)
library(dplyr)

umap_data <- arrow::read_parquet(file.path("../data/first_time/aggregate_umap_embeddings.parquet"))
feature_df <- arrow::read_parquet(file.path("../../4.processing_profiled_features/data/aggregated/live_cell_pyroptosis_wave1_first_time_norm_fs_agg.parquet"))
head(umap_data)

# map the timepoints to the actual hour timepoint
timepoints <- data.frame(
    reference = c("00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17"),
    Metadata_timepoint  = c(1,4,7,10,13,16,19,22,25,28,31,34,37,40,43,46,49,90)
)
# map the timepoints to the main df
umap_data <- umap_data %>% left_join(timepoints, by = c("Metadata_Time" = "reference"))
umap_data$Metadata_timepoint <- as.numeric(umap_data$Metadata_timepoint)
umap_data$Metadata_timepoint_hours <- paste0(umap_data$Metadata_timepoint, " hours")
head(umap_data)

figure_path <- file.path("..","figures","first_time")
# create the output directory if it does not exist
if (!dir.exists(figure_path)) {
  dir.create(figure_path)
}

unique(umap_data$Metadata_treatment)
umap_data$Metadata_treatment <- factor(umap_data$Metadata_treatment, levels = c(
    'Media',
    'DMSO CTL',
    'no Hoechst',

    'LPS 0.1 ug/ml',
    'LPS 1 ug/ml',
    'LPS 10 ug/ml',
    'LPS 1 ug/ml + ATP 2.5 mM',
    'LPS 1 ug/ml + Nigericin 0.1 uM',
    'LPS 1 ug/ml + Nigericin 0.5uM',
    'LPS 1 ug/ml + Nigericin 1 uM',
    'LPS 1 ug/ml + Nigericin 3uM',
    'LPS 1 ug/ml + Nigericin 5uM',

    'Flagellin 0.1 ug/ml',
    'Flagellin 1 ug/ml',
    'Flagellin 10 ug/ml',

    'Thapsigargin 0.5uM',
    'Thapsigargin 1 uM',
    'Thapsigargin 10 uM',
    'H2O2 100 nM',
    'H2O2 100 uM',
    'H2O2 500 uM',

    'Ab1-42 0.4 uM',
    'Ab1-42 2 uM',
    'Ab1-42 10 uM'
))
unique(umap_data$Metadata_treatment)


colorgrad1 <- colorRampPalette(c("lightgrey", "grey"))(3)
# col 2 - 5 hues color ramp 5 hues
colorgrad2 <- colorRampPalette(c("pink", "darkred"))(11)
# col 3 - 3 hues
colorgrad3 <- colorRampPalette(c("yellow", "brown"))(3)
# col 4 - 3 hues
colorgrad4 <- colorRampPalette(c("lightblue", "darkblue"))(6)
# col 5 - 2 hues
colorgrad5 <- colorRampPalette(c("lightgreen", "darkgreen"))(3)
# col 6 - 3 hues
colorgrad6 <- colorRampPalette(c("purple", "#2e004b"))(3)
# col 7 - 2 hues
colorgrad7 <- colorRampPalette(c("cyan", "darkcyan"))(4)
# col 8 - 2 hues
colorgrad8 <- colorRampPalette(c("#ebb676", "darkorange"))(3)
# col 9 - 3 hues
colorgrad9 <- colorRampPalette(c("magenta", "#833b83"))(3)

# define the colors
colors <- c(
    'Media' = colorgrad1[1],
    'DMSO CTL' = colorgrad1[2],
    'no Hoechst' = colorgrad1[3],

    'LPS 0.1 ug/ml' = colorgrad2[1],
    'LPS 1 ug/ml' = colorgrad2[2],
    'LPS 10 ug/ml' = colorgrad2[3],
    'LPS 1 ug/ml + ATP 2.5 mM' = colorgrad2[4],
    'LPS 1 ug/ml + Nigericin 0.1 uM' = colorgrad2[5],
    'LPS 1 ug/ml + Nigericin 0.5uM' = colorgrad2[6],
    'LPS 1 ug/ml + Nigericin 1 uM' = colorgrad2[7],
    'LPS 1 ug/ml + Nigericin 3uM' = colorgrad2[8],
    'LPS 1 ug/ml + Nigericin 5uM' = colorgrad2[9],

    'Flagellin 0.1 ug/ml' = colorgrad5[1],
    'Flagellin 1 ug/ml' = colorgrad5[2],
    'Flagellin 10 ug/ml' = colorgrad5[3],

    'Thapsigargin 0.5uM' = colorgrad8[1],
    'Thapsigargin 1 uM' = colorgrad8[2],
    'Thapsigargin 10 uM' = colorgrad8[3],

    'H2O2 100 nM' = colorgrad7[1],
    'H2O2 100 uM' = colorgrad7[2],
    'H2O2 500 uM' = colorgrad7[3],

    'Ab1-42 0.4 uM' = colorgrad4[1],
    'Ab1-42 2 uM' = colorgrad4[2],
    'Ab1-42 10 uM' = colorgrad4[3]
)

# plot the data
width <- 15
height <- 10
options(repr.plot.width=width, repr.plot.height=height)

umap_plot <- (
    ggplot(umap_data, aes(x=UMAP0, y=UMAP1))
    + geom_point(aes(color=Metadata_treatment), size=1, alpha=0.8)
    + scale_color_manual(
        values = colors
    )
    # move the legend to the bottom
    + guides(
        color = guide_legend(ncol = 5, title = "Treatment", override.aes = list(size = 4, alpha = 1)),
        # move guide title to top
        title.position = "top",
    )

    + theme_bw()
    + theme(
        axis.text.x = element_text(size=14),
        axis.text.y = element_text(size=14),
        axis.title.x = element_text(size=14),
        axis.title.y = element_text(size=14),
        legend.text = element_text(size=14),
        legend.title = element_text(size=14, hjust=0.5),
        legend.position="bottom",
        legend.title.position="top"
    )
    + facet_wrap(~Metadata_timepoint_hours, ncol = 6)
)
png(file.path(figure_path,"umap_plot_facet_time_bulk.png"), width=width, height=height, units="in", res=600)
umap_plot
dev.off()
umap_plot

height <- 10
width <- 10
options(repr.plot.width=width, repr.plot.height=height)
umap_all_time_plot <- (
    ggplot(umap_data, aes(x=UMAP0, y=UMAP1))
    + geom_point(aes(color=Metadata_timepoint), size=2)
    # move the legend to the bottom
    + guides(
        # make the legend a continuous color scale
        color = guide_colorbar(title = "Time"),
        # move guide title to top
        title.position = "top",
        # change size of dots in legend
        override.aes = list(size = 2)    )
    + theme_bw()
    + theme(
        axis.text.x = element_text(size=14),
        axis.text.y = element_text(size=14),
        axis.title.x = element_text(size=14),
        axis.title.y = element_text(size=14),
        legend.text = element_text(size=14),
        legend.title = element_text(size=14, hjust=0.5),
        legend.position="bottom",
        legend.title.position="top"
    )
)
png(file.path(figure_path,"umap_all_time_plot_col_by_treatment_bulk.png"), width=width, height=height, units="in", res=600)
umap_all_time_plot
dev.off()
umap_all_time_plot

width <- 15
height <- 10
options(repr.plot.width=width, repr.plot.height=height)
umap_all_time_plot_facet <- (
    ggplot(umap_data, aes(x=UMAP0, y=UMAP1))
    + geom_point(aes(color=Metadata_timepoint), size=2)
    # move the legend to the bottom
    + guides(
        # make the legend a continuous color scale
        color = guide_colorbar(title = "Time"),
        # move guide title to top
        title.position = "top",
        # change size of dots in legend
        override.aes = list(size = 2)
    )
    + theme_bw()
    + theme(
        axis.text.x = element_text(size=14),
        axis.text.y = element_text(size=14),
        axis.title.x = element_text(size=14),
        axis.title.y = element_text(size=14),
        legend.text = element_text(size=14),
        legend.title = element_text(size=14, hjust=0.5),
        legend.position="bottom",
        legend.title.position="top",
        strip.text = element_text(size = 12)
    )
    + facet_wrap(~Metadata_treatment, ncol = 6)
)
png(file.path(figure_path,"umap_all_time_plot_facet_bulk.png"), width=width, height=height, units="in", res=600)
umap_all_time_plot_facet
dev.off()
umap_all_time_plot_facet

head(feature_df)

library(tidyr)

# drop all metadata columns except for the timepoint, treatment and well
feature_long_df <- feature_df %>% select(-starts_with("Metadata_"))
# add the timepoint and treatment columns to the feature data
feature_long_df$Metadata_timepoint <- feature_df$Metadata_Time
feature_long_df$Metadata_treatment <- feature_df$Metadata_treatment
feature_long_df$Metadata_well <- feature_df$Metadata_Well
head(feature_long_df)



# make the df tidy long with feature value and feature name
feature_long_df <- feature_long_df %>%
    pivot_longer(cols = -c(Metadata_timepoint, Metadata_treatment, Metadata_well), names_to = "feature_name", values_to = "feature_value")
head(feature_long_df)



# get non metadata columns
feature_cols <- colnames(feature_df)[!grepl("Metadata", colnames(feature_df))]
# plot every feature over time for all treatments wells
# make each facet a different feature
width <- 15
height <- 15
options(repr.plot.width=width, repr.plot.height=height)

timelapse_plot <- (
    ggplot(feature_long_df, aes(x=Metadata_timepoint, y=feature_value))
    # + geom_point(aes(color=Metadata_treatment), size=1, alpha=0.8)
    + geom_line(aes(group=Metadata_treatment), linewidth=1, alpha=0.8)
    # + facet_wrap(~feature_name, scales = "free_y", ncol = 4)
    + theme_bw()
    #  + scale_color_manual(
    #     values = colors
    # )

)
timelapse_plot


