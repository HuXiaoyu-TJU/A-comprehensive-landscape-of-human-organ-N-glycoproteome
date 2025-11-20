library(ggplot2)
library(dplyr)
library(readxl)
library(purrr)
library(patchwork)
library(tidyr)

# 读取所有数据文件
file_paths <- c(
  "S1-ANN.xlsx",
  "S2-ANN.xlsx",
  "S3-ANN.xlsx",
  "S4-ANN.xlsx"
)

# 读取并合并所有数据
all_data <- map_df(file_paths, ~read_excel(.x), .id = "Dataset")

# 数据预处理
all_data$`relative abundance` <- as.numeric(all_data$`relative abundance`)
all_data <- all_data %>% filter(`relative abundance` > 0)
all_data$Dataset <- factor(all_data$Dataset, levels = 1:4, labels = paste0("S", 1:4))
all_data$X <- factor(all_data$X, levels = c("mono", "bi", "tri", "tetra"))
all_data$Y <- factor(all_data$Y, levels = unique(all_data$Y))

# 创建主图
main_plot <- ggplot(all_data, aes(x = X, y = Y, size = `relative abundance`, fill = X)) +
  geom_point(shape = 21, color = "black", stroke = 1, alpha = 0.7) +
  scale_size_continuous(range = c(2, 15)) +
  scale_fill_manual(values = c("mono" = "#FDC06F", "bi" = "#A6CEE5", "tri" = "#B2DD8B", "tetra" = "#C2A5CF")) +
  facet_wrap(~ Dataset, ncol = 4, scales = "free_x") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 15),
    axis.text.y = element_text(angle = 0, hjust = 1, size = 15),
    legend.position = "bottom",
    legend.box = "vertical",
    legend.margin = margin(t = 2, r = 0, b = 0, l = 0),
    legend.box.margin = margin(0, 0, 0, 0),
    panel.border = element_rect(color = "black", fill = NA, size = 1),
    strip.background = element_rect(fill = "lightgrey"),
    strip.text = element_text(size = 12, face = "bold"),
    panel.spacing = unit(0, "lines")
  ) +
  guides(fill = guide_legend(title = "Antenna", order = 1),
         size = guide_legend(title = "Relative Abundance", order = 2)
  ) +
  labs(x = "Antenna_number",
       y = "Organ",
       size = "Relative Abundance",    
       fill = "Sample")
main_plot


excel_data <- read_excel("S1-4-ALL-rela.xlsx")


data_long <- excel_data %>%
  pivot_longer(cols = c(S1, S2, S3, S4), names_to = "Stage", values_to = "Cumulativeabundance") %>%
  mutate(Stage = factor(Stage, levels = c("S4", "S3", "S2", "S1")))


stacked_bar_plot <- ggplot(data_long, aes(x = Organ, y = Cumulativeabundance, fill = Stage)) +
  geom_bar(stat = "identity", position = "stack") +
  scale_fill_manual(values = c("S1" = "#E6E1F0", "S2" = "#C5C0E0", "S3" = "#8C8BD0", "S4" = "#3A4CA8")) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 15),
    axis.text.y = element_blank(),
    axis.title.y = element_blank(),
    axis.ticks.y = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.grid.minor.y = element_blank(),
    legend.position = "none",
    plot.margin = margin(t = 35, r = 5, b = 5, l = 0)
  ) +
  labs(x = "Relative Abundance (%)", fill = "Stage") +
  coord_flip()
stacked_bar_plot


combined_plot <- main_plot + stacked_bar_plot + 
  plot_layout(widths = c(4, 1), guides = "collect") & 
  theme(legend.position = "bottom",
        legend.box = "vertical")

print(combined_plot)


ggsave("bubble_plot_with_stacked_bar.svg", 
       combined_plot, width = 10, height = 15)
