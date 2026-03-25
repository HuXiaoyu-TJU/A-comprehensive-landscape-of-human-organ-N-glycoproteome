
# install.packages("UpSetR")
# install.packages("VennDiagram")


library(UpSetR)         
library(VennDiagram) 

upset_dat <- read.delim('forUpset_plot.txt') 

upset_list <- list(upset_dat[,1], 
                   upset_dat[,2], 
                   upset_dat[,3], 
                   upset_dat[,4]   
                   
)   
names(upset_list) <- colnames(upset_dat[1:4])

upset(fromList(upset_list),  
      nsets = 500,     
      nintersects = 11, 
      order.by = "freq", 
      keep.order = F, 
      mb.ratio = c(0.55,0.45),   
      text.scale = 2, 
      main.bar.color = "#FDC06F",
      point.size=2.5, 
      line.size=1.2, 
      mainbar.y.label="Intersection size", 
      sets.x.label="Set size",   
      matrix.color="black", 
      sets.bar.color = "#A6CEE5",
      shade.color="grey70",
      cutoff = 10000,
      show.numbers = "no"
)



unique_elements <- function(set, other_sets) {
  unique_set <- setdiff(set, unlist(other_sets))
  return(unique_set)
}

unique_ids <- list()
for (name in names(upset_list)) {
  other_sets <- upset_list[names(upset_list) != name]
  unique_ids[[name]] <- unique_elements(upset_list[[name]], other_sets)
}

for (name in names(unique_ids)) {
  cat(name, "unique ID count:", length(unique_ids[[name]]), "\n")
}

for (name in names(unique_ids)) {
  filename <- paste0("unique_ids_", name, ".txt")
  write.table(unique_ids[[name]], filename, row.names = FALSE, col.names = FALSE, quote = FALSE)

}

common_ids <- Reduce(intersect, upset_list)
cat("\nCommon IDs present in all four datasets:", length(common_ids), "\n")

write.table(common_ids, "common_ids.txt", row.names = FALSE, col.names = FALSE, quote = FALSE)


all_ids <- unique(unlist(upset_list))

all_ids <- all_ids[all_ids != "" & !is.na(all_ids)]

summary_df <- data.frame(ID = all_ids, stringsAsFactors = FALSE)

for (software_name in names(upset_list)) {
  summary_df[[software_name]] <- ifelse(summary_df$ID %in% upset_list[[software_name]], TRUE, "")
}



write.table(summary_df, 
            file = "ID_Summary_Matrix.csv",
            sep = ",", 
            row.names = FALSE, 
            quote = FALSE, 
            fileEncoding = "GBK")

cat("\nSummary matrix saved.",  "\n")

