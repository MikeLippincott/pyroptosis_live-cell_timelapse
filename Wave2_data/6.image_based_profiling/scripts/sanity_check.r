suppressWarnings(suppressPackageStartupMessages(library(arrow)))
suppressWarnings(suppressPackageStartupMessages(library(dplyr)))
suppressWarnings(suppressPackageStartupMessages(library(ggplot2)))
suppressWarnings(suppressPackageStartupMessages(library(stringr)))
suppressWarnings(suppressPackageStartupMessages(library(tidyr)))

plate_name <- "plate_2"

# find the git root by walking up from the current working directory
find_git_root <- function(start_dir) {
    dir <- start_dir
    while (!dir.exists(file.path(dir, ".git"))) {
        parent <- dirname(dir)
        if (parent == dir) {
            stop("No Git root directory found.")
        }
        dir <- parent
    }
    dir
}
root_dir <- find_git_root(getwd())

# use the Bandicoot mount if it is available, otherwise fall back to the repo's data dir
bandicoot_mount_path <- file.path(Sys.getenv("HOME"), "mnt", "bandicoot")
if (dir.exists(bandicoot_mount_path)) {
    image_base_dir <- file.path(
        Sys.getenv("HOME"), "mnt", "bandicoot",
        "live_cell_timelapse_pyroptosis_project_data"
    )
} else {
    image_base_dir <- file.path(root_dir, "data")
}
image_base_dir <- file.path(image_base_dir, "processed_data")

norm_agg_profiles_path <- file.path(
    image_base_dir, "12.aggregate_profiles", plate_name,
    "aggregate_profiles_from_normalized.parquet"
)
norm_consensus_profiles_path <- file.path(
    image_base_dir, "12.aggregate_profiles", plate_name,
    "consensus_profiles_from_normalized.parquet"
)
fs_agg_profiles_path <- file.path(
    image_base_dir, "12.aggregate_profiles", plate_name,
    "aggregate_profiles_from_feature_selected.parquet"
)
fs_consensus_profiles_path <- file.path(
    image_base_dir, "12.aggregate_profiles", plate_name,
    "consensus_profiles_from_feature_selected.parquet"
)
dir.create(dirname(norm_agg_profiles_path), recursive = TRUE, showWarnings = FALSE)

norm_agg_df <- arrow::read_parquet(norm_agg_profiles_path)

head(norm_agg_df)

unique(norm_agg_df$Metadata_Well)

unique(norm_agg_df$Metadata_Inducer1)

compartment <- "Nuclei"
channels <- c("NucleoLive", "SYTOXGreen")

# build a single treatment-combo label, e.g. "LPS 1ug/ml + Nigericin 1uM"
norm_agg_df <- norm_agg_df %>%
    mutate(
        inducer2_part = if_else(
            Metadata_Inducer2 != "DMSO",
            paste("+", Metadata_Inducer2, Metadata_Inducer2_dose),
            ""
        ),
        Metadata_Treatment_combo = stringr::str_squish(paste(
            Metadata_Inducer1, Metadata_Inducer1_dose,
            inducer2_part,
            "+", Metadata_Inhibitor, Metadata_Inhibitor_dose
        ))
    ) %>%
    select(-inducer2_part)

# sort treatments by the numeric dose values embedded in the label
dose_sort_key <- function(treatment) {
    doses <- as.numeric(str_extract_all(treatment, "[\\d.]+")[[1]])
    if (length(doses) == 0) doses <- 0
    # pad to a fixed width so treatments sort lexicographically on dose magnitude
    paste(sprintf("%020.6f", doses), collapse = "_")
}
treatment_order <- norm_agg_df %>%
    distinct(Metadata_Treatment_combo) %>%
    pull(Metadata_Treatment_combo)
treatment_order <- treatment_order[order(sapply(treatment_order, dose_sort_key))]
norm_agg_df$Metadata_Treatment_combo <- factor(
    norm_agg_df$Metadata_Treatment_combo,
    levels = treatment_order
)

#' Plot mean +/- SE intensity profiles over time, wrapped by treatment with
#' both channels overlaid on each panel
channel_colors <- c("NucleoLive" = "cyan", "SYTOXGreen" = "green")

plot_intensity_profiles <- function(df, compartment, channels, stat, stat_label, ncol = 4) {
    feature_cols <- paste(compartment, "Intensity", stat, channels, sep = "_")
    present <- feature_cols %in% colnames(df)
    feature_cols <- feature_cols[present]
    channels <- channels[present]

    long_df <- df %>%
        select(
            Metadata_Time, Metadata_Treatment_combo, all_of(feature_cols)
        ) %>%
        pivot_longer(
            cols = all_of(feature_cols),
            names_to = "Metadata_Channel",
            values_to = "Intensity"
        ) %>%
        mutate(
            Metadata_Channel = factor(
                feature_cols[match(Metadata_Channel, feature_cols)],
                labels = channels
            )
        )

    summary_df <- long_df %>%
        group_by(Metadata_Treatment_combo, Metadata_Channel, Metadata_Time) %>%
        summarise(
            mean_intensity = mean(Intensity, na.rm = TRUE),
            se_intensity = sd(Intensity, na.rm = TRUE) / sqrt(sum(!is.na(Intensity))),
            .groups = "drop"
        )

    ggplot(
        summary_df,
        aes(x = Metadata_Time, y = mean_intensity, color = Metadata_Channel)
    ) +
        geom_ribbon(
            aes(
                ymin = mean_intensity - se_intensity,
                ymax = mean_intensity + se_intensity,
                fill = Metadata_Channel
            ),
            alpha = 0.2, color = NA
        ) +
        geom_line(linewidth = 1) +
        facet_wrap(~Metadata_Treatment_combo, ncol = ncol) +
        scale_color_manual(values = channel_colors) +
        scale_fill_manual(values = channel_colors) +
        labs(
            title = paste(
                compartment, stat_label,
                "intensity profiles over time, by treatment"
            ),
            x = "Time",
            y = paste(stat_label, "intensity (normalized)"),
            color = "Channel",
            fill = "Channel"
        ) +
        theme_bw(base_size = 22) +
        theme(
            plot.title = element_text(size = 26, face = "bold"),
            axis.title = element_text(size = 24),
            axis.text = element_text(size = 18),
            strip.text = element_text(size = 20),
            legend.title = element_text(size = 22),
            legend.text = element_text(size = 20),
            legend.position = "bottom"
        )
}

options(repr.plot.width = width, repr.plot.height = height)

max_intensity_plot <- plot_intensity_profiles(
    norm_agg_df, compartment, channels, "MaxIntensity", "Max", ncol = ncol
)
max_intensity_plot
