library(educationdata)

# Read in school data
schools_dir <- get_education_data(level = 'schools',
                                  source = 'ccd',
                                  topic = 'directory',
                                  add_labels = TRUE)

# Save dataframe
write.csv(schools_dir,
          "./../../../../large_data/00-raw-data/UI_Education_Data/schools_dir.csv",
          row.names = FALSE)

# Read in school enrollment data
schools_enrollment <- get_education_data(level = 'schools',
                                         source = 'ccd',
                                         topic = 'enrollment',
                                         subtopic = list('race'),
                                         add_labels = TRUE)

# Save dataframe
write.csv(schools_enrollment,
          "./../../../large_data/00-raw-data/UI_Education_Data/schools_enrollment.csv",
          row.names = FALSE)