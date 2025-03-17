suppressWarnings(suppressPackageStartupMessages(library(ggplot2)))
suppressWarnings(suppressPackageStartupMessages(library(cowplot)))
suppressWarnings(suppressPackageStartupMessages(library(dplyr)))
suppressWarnings(suppressPackageStartupMessages(library(arrow)))
suppressWarnings(suppressPackageStartupMessages(library(argparse)))
suppressWarnings(suppressPackageStartupMessages(library(gifski)))
if (!requireNamespace("gganimate", quietly = TRUE)) {
  install.packages("gganimate")
}
suppressWarnings(suppressPackageStartupMessages(library(gganimate)))

data_set <- "first_time"

input_data_path <- file.path("..","data",data_set)

# set the path to the data to visualize
umap_data_path <- file.path(input_data_path,"umap_embeddings.parquet")
pca_data_path <- file.path(input_data_path,"pca_embeddings.parquet")
scree_data_path <- file.path(input_data_path,"scree_plot.parquet")

# read the data
umap_data <- arrow::read_parquet(umap_data_path)
pca_data <- arrow::read_parquet(pca_data_path)
scree_data <- arrow::read_parquet(scree_data_path)

# sample from well, fov, and time
dim(umap_data)
umap_data <- umap_data %>%
  group_by(Metadata_Well, Metadata_FOV, Metadata_Time) %>%
  sample_n(4) %>%
  ungroup()
dim(umap_data)

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

figure_path <- file.path("..","figures",data_set)
# create the output directory if it does not exist
if (!dir.exists(figure_path)) {
  dir.create(figure_path)
}

head(umap_data)


wells <- unique(umap_data$Metadata_Well)
# sort the wells alphabetically
wells <- sort(wells)

print(dim(umap_data))
print(dim(pca_data))
print(dim(scree_data))

head(umap_data,1)
head(pca_data,1)
head(scree_data,1)

print(dim(umap_data))
print(dim(pca_data))

# randomly mix the order of the rows to prevent plotting bias and artifacts
umap_data <- umap_data[sample(nrow(umap_data)),]
pca_data <- pca_data[sample(nrow(pca_data)),]

print(dim(umap_data))
print(dim(pca_data))

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




# 9 colors
# col 1 - 3 hues
# colorgrad1 <- c("white", "grey", "#585858")
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

# order the df by time
umap_data <- umap_data %>% arrange(Metadata_Time)
head(umap_data)

name_repair_function <- function(names) {
  names[1] <- paste0(names[1], "_original")
  return(names)
}
df_background <- tidyr::crossing(
    umap_data,
    Metadata_treatment = unique(umap_data$Metadata_treatment),
    .name_repair = name_repair_function
)
head(df_background)

# get the centroids of each treatment, at each timepoint
centroids <- umap_data %>%
  group_by(Metadata_treatment, Metadata_timepoint) %>%
  summarize(
    UMAP0 = mean(UMAP0),
    UMAP1 = mean(UMAP1)
  ) %>%
  ungroup()
head(centroids)



# plot the centroids over time
width <- 10
height <- 10
options(repr.plot.width=width, repr.plot.height=height)
centroids_umap_plot <- (
    # plot the whole dataset in grey with low alpha
    ggplot(centroids, aes(x=UMAP0, y=UMAP1))
    + geom_point(
        data = df_background,
        color = "lightgrey",
        size = 0.5,
        alpha = 0.1
    )
    + geom_point(aes(color=Metadata_treatment), size=1.5, alpha=0.9)

    + scale_color_manual(
        values = colors
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
    + transition_time(Metadata_timepoint)
    + labs(title = "Time: {frame_time}")
)

n_timepoints <- length(unique(centroids$Metadata_timepoint))
fps <- 15

nframes <- n_timepoints * fps



anim_save(
    "../figures/pyroptosis_timelapsed_centroids.gif",
    animate(
        centroids_umap_plot,
        fps = fps,
        nframes = nframes,
        width = width,
        height = height,
        units = "in",
        res = 600
        ))


# plot the centroids over time
width <- 30
height <- 30
options(repr.plot.width=width, repr.plot.height=height)
centroids_umap_plot <- (
    # plot the whole dataset in grey with low alpha
    ggplot(centroids, aes(x=UMAP0, y=UMAP1))
    + geom_point(
        data = df_background,
        color = "lightgrey",
        size = 0.5,
        alpha = 0.1
    )
    + geom_point(aes(color=Metadata_treatment), size=1.5, alpha=0.9)

    + scale_color_manual(
        values = colors
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
    + facet_wrap(~Metadata_treatment, ncol = 6)
    + transition_time(Metadata_timepoint)
    + labs(title = "Time: {frame_time}")
)

n_timepoints <- length(unique(centroids$Metadata_timepoint))
fps <- 15

nframes <- n_timepoints * fps


anim_save(
    "../figures/pyroptosis_timelapsed_centroids_facet_by_treatment.gif",
    animate(
        centroids_umap_plot,
        fps = fps,
        nframes = nframes,
        width = width,
        height = height,
        units = "in",
        res = 600
        ))
