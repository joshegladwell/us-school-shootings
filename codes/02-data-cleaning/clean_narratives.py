import pandas as pd
import numpy as np

# Read in school shooting database incidents
SSDB = pd.read_csv('../../data/02-clean-data/SSDB/incident.csv')

# Save narrative text data from each incident
narratives = SSDB['Narrative'].replace(np.nan, "Nan").tolist()

# We will treat the level of media attention as the label
labels = SSDB['Media_Attention'].tolist()

# Perform count vectorization on each incident's narrative
from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(stop_words='english')
X = vectorizer.fit_transform(narratives)

# Organize sparse count matrix into dataframe, include labels column
token_counts = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
token_counts['y_label'] = labels
token_counts['narrative_texts'] = narratives

# Save to CSV
token_counts.to_csv('../../data/02-clean-data/SSDB/narrative_vectors.csv', index=False)


