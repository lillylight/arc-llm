# Setting Up Arc LLM on GitHub

This guide will help you push your Arc LLM project to GitHub and set it up so that others can use it directly from Google Colab.

## 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in to your account (or create one if you don't have it).
2. Click on the "+" icon in the top right corner and select "New repository".
3. Name your repository "arc-llm".
4. Add a description: "A project that integrates Claude API with SpatialLM to convert text descriptions into 2D and 3D visualizations."
5. Choose "Public" visibility (so others can access it from Colab).
6. Do NOT initialize the repository with a README, .gitignore, or license (since we already have these files).
7. Click "Create repository".

## 2. Push Your Local Repository to GitHub

After creating the repository, GitHub will show you commands to push an existing repository. Follow these steps:

```bash
# Make sure you're in the arc-llm directory
cd arc-llm

# Set the remote URL (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/arc-llm.git

# Push the repository to GitHub
git push -u origin main
```

If you're using a different branch name (like "master" instead of "main"), replace "main" with your branch name.

## 3. Update the Colab Runner

After pushing to GitHub, you need to update the Colab runner notebook to use your GitHub repository:

1. Open the `colab_runner.ipynb` file.
2. Find the line that says `!git clone https://github.com/YOUR_USERNAME/arc-llm.git`.
3. Replace `YOUR_USERNAME` with your actual GitHub username.
4. Save the file.
5. Commit and push the changes:

```bash
git add colab_runner.ipynb
git commit -m "Update Colab runner with correct GitHub username"
git push
```

## 4. Using Arc LLM in Google Colab

There are two ways to use Arc LLM in Google Colab:

### Option 1: Direct Link to the Colab Runner

1. Go to your GitHub repository.
2. Navigate to the `colab_runner.ipynb` file.
3. Click on the "Open in Colab" button (if it appears).
4. If the button doesn't appear, you can manually open it in Colab:
   - Copy the URL of the raw file: `https://raw.githubusercontent.com/YOUR_USERNAME/arc-llm/main/colab_runner.ipynb`
   - Go to [Google Colab](https://colab.research.google.com/)
   - Click on "File" > "Open notebook"
   - Select the "GitHub" tab
   - Paste the URL and click "Search"
   - Click on the notebook that appears

### Option 2: GitHub Import in Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click on "File" > "Open notebook"
3. Select the "GitHub" tab
4. Enter your GitHub username and select the "arc-llm" repository
5. Select the "colab_runner.ipynb" file

## 5. Sharing with Others

To share Arc LLM with others, you can:

1. Share the link to your GitHub repository
2. Share a direct link to the Colab notebook: `https://colab.research.google.com/github/YOUR_USERNAME/arc-llm/blob/main/colab_runner.ipynb`
3. Add a "Open in Colab" badge to your README.md:

```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/arc-llm/blob/main/colab_runner.ipynb)
```

Replace `YOUR_USERNAME` with your actual GitHub username.
