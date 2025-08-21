# Troubleshooting Guide

## Audio File Loading Issues

### Common Problems:

1. **File Size Limitations**: GitHub Pages has a 100MB file size limit per repository. Some audio files are quite large (7MB+).

2. **CORS Issues**: GitHub Pages may have CORS restrictions for audio files.

3. **File Path Issues**: Ensure audio files are in the correct `docs/audio/` directory.

4. **Character Encoding**: Some filenames contain special characters that may cause issues.

### Solutions:

1. **Reduce Audio File Sizes**:
   - Convert to lower bitrate (128kbps instead of 320kbps)
   - Use shorter audio clips (30 seconds instead of full songs)
   - Consider using compressed formats like AAC

2. **Use CDN for Large Files**:
   - Upload large audio files to a CDN (AWS S3, Google Cloud Storage)
   - Update the audio metadata to point to CDN URLs

3. **Check File Accessibility**:
   - Visit `test-audio.html` to check if files are accessible
   - Check browser console for specific error messages

## YouTube Video Issues

### Common Problems:

1. **Placeholder Video IDs**: Some videos use placeholder IDs that don't work.
2. **Embedding Restrictions**: Some videos may have embedding disabled.
3. **Autoplay Restrictions**: Modern browsers block autoplay.

### Solutions:

1. **Update Video IDs**: Replace placeholder IDs with actual YouTube video IDs.
2. **Check Embedding**: Ensure videos allow embedding.
3. **Add Error Handling**: Show fallback content when videos fail to load.

## Debugging Steps

1. **Open Browser Console**: Press F12 and check for error messages.
2. **Visit Debug Page**: Go to `debug.html` to test audio and video loading.
3. **Check Network Tab**: Look for failed requests in the Network tab.
4. **Test Locally**: Run a local server to test without GitHub Pages restrictions.

## File Structure

Ensure your files are organized correctly:

```
docs/
├── index.html
├── script.js
├── styles.css
├── audio_metadata.json
├── audio/
│   ├── suno_v4_5_2023_4_Taylor_Swift_Anti-Hero.mp3
│   ├── YuE_1957_1_Elvis_Presley_All_Shook_Up.mp3
│   └── ...
└── .nojekyll
```

## GitHub Pages Configuration

- Ensure `.nojekyll` file is present in the `docs/` directory
- Check that the repository is set to deploy from the `docs/` folder
- Verify that the GitHub Actions workflow is working correctly

## Alternative Solutions

If audio files continue to have issues:

1. **Use External Hosting**: Host audio files on a dedicated audio hosting service
2. **Use Audio Streaming**: Consider using a streaming service API
3. **Reduce Dependencies**: Focus on YouTube videos for Billboard songs and smaller audio files for AI-generated content
