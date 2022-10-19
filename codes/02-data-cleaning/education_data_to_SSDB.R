# IMPORTANT: This script relies on the datasets produced by clean_databases.R
# (in this current directory) and education_data_query.R (in
# codes/01-data-gathering/APIs). Ensure that those have been run before
# running this script.
library(dplyr)

# Read in the incidents table
incidents <- read.csv('./../../data/02-clean-data/SSDB/incident.csv') %>%
  # Add new column for ncessch, add pseudo-id column to connect with ccd dir
  mutate(ncessch = NA,
         hs_flag = ifelse(School_Level == "High", 1, 0),
         new_id = paste0(
           Year,
           tolower(State),
           tolower(gsub(" ", "", City)),
           substr(tolower(gsub(" ", "", School)), 1, 5),
           hs_flag
         ))

# The goal here is to add a ncessch key to the incidents table to get more
# information about each school. We will do this by creating our own key from
# the common information between the incidents table and the ccd directories.

# To start, we need to build a state lookup table to be able to get the
# abbreviations from state names
states <- c("Alabama", "Alaska", "American Samoa", "Arizona", "Arkansas",
            "California", "Colorado", "Connecticut", "Delaware",
            "District of Columbia", "Florida", "Georgia", "Guam", "Hawaii",
            "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
            "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
            "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
            "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
            "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
            "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina",
            "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
            "Virginia", "Virgin Islands of the US", "Washington",
            "West Virginia", "Wisconsin", "Wyoming"
)
states_lookup <- c("AL", "AK", "AS", "AZ", "AR", "CA", "CO", "CT", "DE", "DC",
                   "FL", "GA", "GU", "HI", "ID", "IL", "IN", "IA", "KS", "KY",
                   "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE",
                   "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR",
                   "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", 
                   "VI", "WA", "WV", "WI", "WY")
names(states_lookup) <- states

# Define years that the directories exist for
ncessch_years = seq(1986, 2020)

# Cycle through each year defined above
for (yr in ncessch_years) {
  print(paste("Retrieving ncessch IDs from", yr))
  # Read in the directory for the given year
  directory <- read.csv(
    paste0('./../../../large_data/00-raw-data/UI/ccd_dirs/dir_',
           as.character(yr),
           '.csv')
  )
  
  # Save state abbreviations from directory
  dir_states <-  tolower(states_lookup[directory$fips])
  
  # Save lowercased and non-spaced cities from directory
  dir_cities <- tolower(gsub(" ", "", directory$city_mailing))
  
  # Save lowercased and non-spaced school names from directory
  dir_school <- tolower(gsub(" ", "", directory$school_name))
  
  # Save first five characters of school names from directory
  dir_school_trunc <- substr(dir_school, 1, 5)
  
  # Generate flag (1 if school in dir is high school, else 0)
  dir_hs_flag <- ifelse(directory$highest_grade_offered == "12", 1, 0)
  
  # Generate new pseudo-id column to connect directory with incidents table
  directory$new_id <- paste0(
    directory$year,
    dir_states,
    dir_cities,
    dir_school_trunc,
    dir_hs_flag
  )
  
  # Retrieve new_ids from incidents for given year
  inc_year <- incidents %>%
    filter(Year == yr)
  
  # Check each pseudo-id from the incident table for the given year against
  # the pseudo-ids in the directory for the given year
  for (inc_new_id in inc_year$new_id) {
    # Ensure that the pseudo-id from the incident table exists in the directory
    if (inc_new_id %in% directory$new_id) {
      # Save ncessch_id from matching directory entry
      ncessch_id <- directory[directory$new_id == inc_new_id,]$ncessch

      # Assign ncessch_id from directory to ncessch_id column in incidents
      # table only if there was one ncessch_id match
      if (length(ncessch_id) == 1) {
        incidents[incidents$new_id == inc_new_id,]$ncessch <- ncessch_id
      }
    }
  }
}

# Remove pseudo-id and hs_flag from incidents table
incidents$hs_flag <- NULL
incidents$new_id <- NULL

# Save incidents table to csv
write.csv(incidents,
          './../../data/02-clean-data/SSDB/incident_ncessch.csv',
          row.names = FALSE)
