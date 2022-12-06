# SYNC LOCAL VERSION OF WEBSITE TO GU-DOMAINS SERVER
rsync -alvr --delete 501-project-website gladwell@gladwell.georgetown.domains:/home/gladwell/public_html/

# PUSH GIT REPO TO THE CLOUD FOR BACKUP
echo Commit message: ;
read message;
echo "commit message = "$message; 
git add ./; 
git commit -m "$message"; 
git push
