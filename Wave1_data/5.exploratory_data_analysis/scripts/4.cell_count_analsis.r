suppressWarnings(suppressPackageStartupMessages(library(ggplot2)))
suppressWarnings(suppressPackageStartupMessages(library(dplyr)))

columns <- c(
    "Metadata_treatment",
    "Metadata_Well",
    "Metadata_number_of_singlecells",
    "Metadata_FOV",
    "Metadata_treatment1",
    "Metadata_Time",
    "Metadata_treatment2",
    "Metadata_treatment1_dose",
    "Metadata_treatment1_unit",
    'Metadata_treatment2_dose',
    "Metadata_treatment2_unit",
    "Metadata_serum",
    "Metadata_ImageNumber",
    "Metadata_Cells_Number_Object_Number",
    "Metadata_Cytoplasm_Parent_Cells",
    "Metadata_Cytoplasm_Parent_Nuclei",
    "Metadata_ImageNumber_1",
    "Metadata_ImageNumber_2",
    "Metadata_ImageNumber_3",
    "Metadata_Nuclei_Number_Object_Number"
)

df <- file.path("../../4.processing_profiled_features/data/preprocessed_data/live_cell_pyroptosis_wave1_sc_first_time_norm_fs.parquet")

df <- arrow::read_parquet(df,col_select = columns)
df$well_fov <- paste0(df$Metadata_Well, "_", df$Metadata_FOV)
df$Metadata_timpoint <- as.numeric(df$Metadata_Time) * 3 # 3 hours
df$unique_cell <- paste0(df$Metadata_timpoint, "_", df$well_fov, "_", df$Metadata_ImageNumber, "_", df$Metadata_Nuclei_Number_Object_Number)
df$unique_well <- paste0(df$well_fov, "_", df$Metadata_treatment)
# show all columns in a jupyter notebooks
print(dim(df))
head(df)

# get the cell counts per well per time
cell_counts <- df %>%
  group_by(unique_well,Metadata_treatment, Metadata_timpoint) %>%
  # get the unique cell count per well per time
    summarise(cell_count = n_distinct(unique_cell)) %>%
    ungroup()

head(cell_counts)

unique(cell_counts$Metadata_treatment)

cell_counts$Metadata_treatment <- factor(cell_counts$Metadata_treatment, levels=c(
    'DMSO CTL',
    'Media',
    'Ab1-42 0.4 uM',
    'Ab1-42 2 uM',
    'Ab1-42 10 uM',
    'Flagellin 0.1 ug/ml',
    'Flagellin 1 ug/ml',
    'Flagellin 10 ug/ml',
    'H2O2 100 nM',
    'H2O2 100 uM',
    'H2O2 500 uM',
    'LPS 0.1 ug/ml',
    'LPS 1 ug/ml',
    'LPS 1 ug/ml + ATP 2.5 mM',
    'LPS 1 ug/ml + Nigericin 0.1 uM',
    'LPS 1 ug/ml + Nigericin 0.5uM',
    'LPS 1 ug/ml + Nigericin 1 uM',
    'LPS 1 ug/ml + Nigericin 3uM',
    'LPS 1 ug/ml + Nigericin 5uM',
    'LPS 10 ug/ml',
    'Thapsigargin 0.5uM',
    'Thapsigargin 1 uM',
    'Thapsigargin 10 uM'
))
unique(cell_counts$Metadata_treatment)

width <- 20
height <- 20
options(repr.plot.width=width, repr.plot.height=height)
# plot the timelapse _profiles for a given feature
timelapse_plot <- (
    # group the timepoints by the feature
    ggplot(cell_counts, aes(x=Metadata_timpoint, y=cell_count), fill=Metadata_treatment)
    + geom_line(aes(group=unique_well, color=Metadata_treatment), alpha=0.9, linewidth=1)
    # add a sd ribbon to the plot

    + theme_bw()

    + theme(
        axis.text.x = element_text(angle = 45, hjust = 1, size = 16),
        axis.text.y = element_text(size = 16),
        axis.title = element_text(size = 20),
        legend.title = element_text(size = 20),
        legend.text = element_text(size = 16),
        legend.position = "none"
    )
    + labs(
        x = "Time (h)",
        y = "Cell count"
    )
    + facet_wrap(~Metadata_treatment, scales="free_y", ncol=3)
)
timelapse_plot

# save the plot
ggsave(file.path("../figures","cell_count_timelapse.png"), timelapse_plot, width=width, height=height, dpi=600)

# get the last timepoint for each well and treatment
cell_counts %>%
    group_by(unique_well) %>%
    filter(Metadata_timpoint == max(Metadata_timpoint)) %>%
    filter(Metadata_treatment == "DMSO CTL") %>%
    ungroup() %>%
    arrange(desc(cell_count)) %>%
    head(50)

# get the

# width <- 20
# height <- 10
# options(repr.plot.width=width, repr.plot.height=height)
# # plot the timelapse _profiles for a given feature
# cell_count_difference_plot <- (
#     # group the timepoints by the feature
#     ggplot(df, aes(x=Metadata_treatment, y=cell_count), fill=Metadata_treatment)
#     # bar plot for the cell counts per well per time
#     + geom_bar(stat="identity", position="dodge", aes(fill=Metadata_treatment))
#     + theme_bw()
#     + theme(
#         legend.position = "none",
#         axis.text.x = element_text(angle = 45, hjust = 1, size = 16),
#         axis.text.y = element_text(size = 16),
#         axis.title = element_text(size = 20)
#     )

#     + labs(x="Treatment", y="Cell count difference\n between first and last time point")
# )
# cell_count_difference_plot
# ggsave(file.path("../figures","cell_count_difference.png"), cell_count_difference_plot, width=width, height=height, dpi=600)
