library(ggplot2)
library(ComplexUpset)


fu <- read.table('upsetplot_test.txt',header = 1,sep = '\t')

fu[1:5,1:5]

groups <- colnames(fu)[3:20]
groups

upset_plot<-upset(
  fu,
  groups,
  name = 'groups',
  n_intersections = 40,
  width_ratio = 0.2,
  height_ratio = 1.3, 
  stripes='white',
  base_annotations = list(
    'Intersection size' = intersection_size(
      counts = FALSE,
      mapping = aes(fill = Class),
       ) + 
      scale_fill_manual(values = c(
      'Hybrid' = '#A6CEE5', 'Complex' = '#FDC06F',
      'High-mannose' = '#B2DD8B'
    )) +theme(
      panel.grid.major = element_line(color = "gray90", linewidth = 0.5),
      panel.grid.minor = element_blank(),
      axis.text = element_text(size = 14),
      axis.title = element_text(size = 14),
      legend.position = "none"
    ) + scale_y_continuous(breaks = seq(0, 3500, by = 1000))
  ),

  set_sizes = (
    upset_set_size() +
      theme(
        axis.text.x = element_text(angle = 90, size = 14),
        axis.title = element_text(size = 14)
      )
  ),

  
  matrix = intersection_matrix(
    geom = geom_point(
      size = 1,  
      stroke = 0.6  
    ),
    segment = geom_segment(
      linewidth = 0.8,  
      color = "black"  
    )
  )

)

print(upset_plot)

final_plot <- upset_plot + theme(
  text = element_text(size = 14),  
  axis.text = element_text(size = 14),
  axis.title = element_text(size = 14),
  legend.text = element_text(size = 14),
  legend.title = element_text(size = 14),
  plot.title = element_text(size = 14)
)
print(final_plot)


ggsave("final_plot_landscape.tiff", final_plot, width = 297, height = 210, units = "mm", dpi = 600)


library(dplyr)
library(tidyr)

organ_data <- fu[, 3:20]

class_data <- fu$Class

get_intersections <- function(data) {
  apply(data, 1, function(row) {
    intersection <- colnames(data)[row]
    if (length(intersection) > 0) {
      paste(intersection, collapse = "&")
    } else {
      "None"
    }
  })
}

intersections <- get_intersections(organ_data)

intersection_elements <- data.frame(
  intersection = intersections,
  ID = fu$ID,
  Class = class_data,
  stringsAsFactors = FALSE
)

intersection_summary <- intersection_elements %>%
  group_by(intersection) %>%
  summarise(
    size = n(),
    IDs = list(ID),
    Classes = list(Class)
  ) %>%
  arrange(desc(size)) %>%
  slice_head(n = 45) %>%  
  mutate(rank = row_number())  


dir.create("intersection_outputs", showWarnings = FALSE)

for (i in 1:nrow(intersection_summary)) {
  intersection_name <- intersection_summary$intersection[i]
  ids <- unlist(intersection_summary$IDs[i])
  classes <- unlist(intersection_summary$Classes[i])
  rank <- intersection_summary$rank[i]
  

  output_df <- data.frame(ID = ids, Class = classes)

  file_name <- gsub("&", "_", intersection_name)

  file_name <- paste0(sprintf("%02d", rank), "_", file_name)
  
  write.csv(output_df, file = paste0("intersection_outputs/", file_name, ".csv"), row.names = FALSE)
}

summary_output <- intersection_summary %>%
  select(rank, intersection, size) %>%
  arrange(rank)

write.csv(summary_output, "intersection_summary.csv", row.names = FALSE)

print("Complete.Please read 'intersection_outputs' folder.")



library(dplyr)
library(ggplot2)

color_scheme <- c('Hybrid' = '#A6CEE5', 'Complex' = '#FDC06F', 'High-mannose' = '#B2DD8B')


dir.create("pie_charts", showWarnings = FALSE)

for (i in 20:40) {
  intersection_name <- intersection_summary$intersection[i]
  ids <- unlist(intersection_summary$IDs[i])
  classes <- unlist(intersection_summary$Classes[i])
  rank <- intersection_summary$rank[i]
  
  class_percentages <- table(classes) / length(classes) * 100

  plot_data <- data.frame(
    Class = names(class_percentages),
    Percentage = as.numeric(class_percentages)
  )
  
  p <- ggplot(plot_data, aes(x = "", y = Percentage, fill = Class)) +
    geom_bar(stat = "identity", width = 1) +
    coord_polar("y", start = 0) +
    scale_fill_manual(values = color_scheme) +
    theme_void() +
    theme(legend.position = "none") +
    labs(title = NULL,
         fill = "Class")
  

  ggsave(filename = paste0("pie_charts/", sprintf("%02d", rank), "_", gsub("&", "_", intersection_name), "_pie.tiff"),
         plot = p, width = 8, height = 8, units = "in", dpi = 600)
  
  print(paste("done：", intersection_name))
}

print("Complete, please read 'pie_charts' folder.")
