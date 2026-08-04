# Adding an Infographic to the Website

Once you have a finished HTML infographic, follow these steps to publish it on the SME&C Infographic Hub. Everything is done through the GitHub website — no command-line tools required.

## 1. Fork the Repository

Since you won't have direct edit access, you'll work from your own copy (a "fork") of the repository.

1. Go to the repository on GitHub
2. Click the **Fork** button in the top-right corner of the page
3. On the "Create a new fork" page, leave the defaults and click **Create fork**
4. GitHub will create a copy of the repository under your account and take you there

> You only need to fork once. If you've already forked the repository, go to your fork on GitHub and click **Sync fork** → **Update branch** to make sure it's up to date before uploading.

## 2. Navigate to the Correct Category Folder

In **your fork**, open the folder that matches your infographic's topic:

| Folder | Category |
|---|---|
| `azure-databases/` | Azure Databases |
| `fabric/` | Fabric |
| `foundry/` | Foundry |
| `github-copilot/` | GitHub Copilot |
| `avd/` | AVD |
| `app-platform-services/` | App Platform Services |
| `azure-openai/` | Azure OpenAI |
| `defender-for-cloud/` | Defender for Cloud |

Click on the folder name to open it.

## 3. Upload Your HTML File

1. In the category folder, click the **Add file** button (top-right) and select **Upload files**
2. Drag your `.html` file onto the upload area, or click **choose your files** to browse for it
3. Make sure the file name uses kebab-case (e.g., `sql-migration-guide.html`)
4. Add a short commit message like *"Add SQL migration guide infographic"*
5. Leave **Commit directly to the `main` branch** selected (this is your fork, so it's safe)
6. Click **Commit changes**

## 4. Open a Pull Request

Now you'll send your changes back to the original repository:

1. Go back to the main page of **your fork**
2. You should see a banner saying your branch is ahead — click **Contribute** → **Open pull request**
3. GitHub will show you a comparison between your fork and the original repository
4. Add a title and any helpful details in the description
5. Click **Create pull request**

Once a maintainer reviews and merges your PR, the website will automatically update and your infographic will appear on the site.

## That's It!

You only need to fork the repo, upload the HTML file to the right folder, and open a PR. The manifest and site are updated automatically when your PR is merged.
