library(educationdata)

# Create list of all years in ccd education directory
ccd_years <- as.character(seq(1986, 2020))

# Cycle through all years and save each directory as csv
for (yr in ccd_years) {
  # Read in school data
  schools_dir <- get_education_data(level = 'schools',
                                    source = 'ccd',
                                    topic = 'directory',
                                    filters = list(year = yr),
                                    add_labels = TRUE)
  
  # Write csv
  write.csv(schools_dir,
            paste0(
              "./../../../../../large_data/00-raw-data/UI/ccd_dirs/dir_",
              yr,
              ".csv"
            ),
            row.names = FALSE)
}
