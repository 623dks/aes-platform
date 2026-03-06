import pandas as pd

# Load your data
df = pd.read_csv('/home/g623dks/data/raw/train.csv')

# Keyword mapping to identify the 'Exam Type' (Prompt)
def get_essay_set(text):
    text = str(text).lower()
    if "driverless" in text or "autonomous" in text: return 1
    if "venus" in text: return 2
    if "cowboy" in text or "seagoing" in text or "crew" in text: return 3
    if "face" in text or "mars" in text or "aliens" in text: return 4
    if "electoral" in text or "college" in text or "vote" in text: return 5
    if "car" in text or "free" in text or "limitation" in text: return 6
    if "facial" in text or "action" in text or "emotion" in text: return 7
    return 0 

# Apply the mapping
df['essay_set'] = df['full_text'].apply(get_essay_set)

# Save it to a NEW file so we don't mess up the raw data
df.to_csv('/home/g623dks/data/raw/train_labeled.csv', index=False)

print("Data Labeled Successfully!")
print("Counts per set:")
print(df['essay_set'].value_counts())
