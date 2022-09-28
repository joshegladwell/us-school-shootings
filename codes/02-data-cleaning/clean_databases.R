# Import libraries
library(tidyverse)

# Read in data
data_path <- "../../data/01-modified-data/"
shooters_MS <- read.csv(paste0(data_path, "MSDB/mass_shooter_database.csv"),
                     skip = 1)
incident_SS <- read.csv(paste0(data_path, "SSDB/incident.csv"))
shooters_SS <- read.csv(paste0(data_path, "SSDB/shooter.csv"))

# There appears to be a duplicate Incident_ID in the school shooting DB
#incident_SS[duplicated(incident_SS$Incident_ID),]$Incident_ID

# The id in question is 20210902CASAL. Viewing the details...
#View(incident_SS[incident_SS$Incident_ID == "20210902CASAL",])

# On further research, the second record with the duplicate id seems to have
# been based on a misinformed article (it no longer exists, whereas the story
# given in the first record is still posted on multiple local news sites)

# Remove duplicate row
incident_SS <- incident_SS[-286,]

write.csv(incident_SS, "../../data/02-clean-data/SSDB/incident.csv",
          row.names = FALSE)


# In the mass shooter DB, we will filter the data down to only school shootings
# and we will generate an id that can connect the incidents/cases to the school
# shooting DB
shooters_clean_MS <- shooters_MS %>%
  # Filter on locations of 0 (K-12 schools) and 1 (colleges/universities)
  filter(Location == 0 | Location == 1 |
           Other.Location == 0 | Other.Location == 1) %>%
  mutate(Incident_ID_partial = sprintf("%04d%02d%02d%s",
                                       Year,
                                       Month,
                                       Day,
                                       State))

# Create incident key in MSDB
# Save incident ids from SSDB
incident_ids <- incident_SS$Incident_ID

# Save partial incident IDs
partial_ids <- shooters_clean_MS$Incident_ID_partial

# Complete partial ids if they match an incident id in SSDB
for (i in 1:length(partial_ids)) {
  completed_id <- incident_ids[grepl(partial_ids[i], incident_ids, fixed = TRUE)]
  
  if (identical(completed_id, character(0))) {
    partial_ids[i] <- "NA"
  }
  else {
    partial_ids[i] <- completed_id
  }
}

# Save completed IDs to shooters_clean_MS, reorder columns, drop partial ids
shooters_clean_MS <- shooters_clean_MS %>%
  mutate(Incident_ID = partial_ids) %>%
  select(c(-Incident_ID_partial)) %>%
  relocate(Incident_ID)

write.csv(shooters_clean_MS,
          "../../data/02-clean-data/MSDB/school_shooters.csv",
          row.names = FALSE)

# Now let's take a closer look at the shooters that aren't present in SSDB and
# ascertain why
SS_missing <- shooters_clean_MS[shooters_clean_MS$Incident_ID =="NA",]
write.csv(SS_missing,
          "../../data/02-clean-data/missing_shooters.csv",
          row.names = FALSE)


#######
# For printing tables in html
# library(xtable)
# print(xtable(incident_SS[incident_SS$Incident_ID == "20210902CASAL",]), type = "html")

# For context/information on data_cleaning.html
# How many total shooters are listed in MSDB?
# nrow(shooters_MS)
# 351

# How many school shooters are listed in MSDB?
# nrow(shooters_clean_MS)
# 24

# How many of the school shooters in MSDB are also listed in SSDB?
# nrow(shooters_clean_MS[shooters_clean_MS$Incident_ID !="NA",])
# 14
#######