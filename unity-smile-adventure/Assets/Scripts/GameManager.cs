using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class GameManager : MonoBehaviour
{
    // Singleton instance
    public static GameManager Instance { get; private set; }

    // Game state
    [System.Serializable]
    public class GameState
    {
        public int currentLevel = 1;
        public int totalScore = 0;
        public string playerName;
    }

    [Header("Game Settings")]
    public GameState gameState = new GameState();
    public bool isPaused = false;

    [Header("UI References")]
    public TextMeshProUGUI scoreText;
    public TextMeshProUGUI levelText;
    public GameObject pauseMenu;
    public GameObject gameOverMenu;

    [Header("Audio")]
    public AudioClip backgroundMusic;
    public AudioClip successSound;
    public AudioClip failSound;

    // Events
    public delegate void GameEvent();
    public event GameEvent OnGameStart;
    public event GameEvent OnGamePause;
    public event GameEvent OnGameResume;
    public event GameEvent OnGameOver;
    public event GameEvent OnLevelComplete;

    // Mobile integration
    private bool isReactNativeInitialized = false;

    private void Awake()
    {
        // Singleton pattern
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
            return;
        }

        // Initialize game
        InitializeGame();
    }

    private void InitializeGame()
    {
        // Set UI elements
        UpdateUI();

        // Initialize audio
        if (backgroundMusic != null)
        {
            // Setup background music
            AudioSource audioSource = GetComponent<AudioSource>();
            if (audioSource != null)
            {
                audioSource.clip = backgroundMusic;
                audioSource.loop = true;
                audioSource.Play();
            }
        }

        // Listen for React Native messages
        // This would be implemented with a plugin
        ListenForReactNativeMessages();

        // Fire game start event
        OnGameStart?.Invoke();
    }

    public void PauseGame()
    {
        isPaused = true;
        Time.timeScale = 0;
        if (pauseMenu != null)
        {
            pauseMenu.SetActive(true);
        }
        OnGamePause?.Invoke();
    }

    public void ResumeGame()
    {
        isPaused = false;
        Time.timeScale = 1;
        if (pauseMenu != null)
        {
            pauseMenu.SetActive(false);
        }
        OnGameResume?.Invoke();
    }

    public void GameOver()
    {
        if (gameOverMenu != null)
        {
            gameOverMenu.SetActive(true);
        }
        OnGameOver?.Invoke();

        // Send score to React Native
        SendScoreToReactNative();
    }

    public void CompleteLevel()
    {
        gameState.currentLevel++;
        OnLevelComplete?.Invoke();
        UpdateUI();

        // Send progress to React Native
        SendProgressToReactNative();
    }

    public void AddScore(int points)
    {
        gameState.totalScore += points;
        UpdateUI();
    }

    private void UpdateUI()
    {
        if (scoreText != null)
        {
            scoreText.text = "Score: " + gameState.totalScore.ToString();
        }

        if (levelText != null)
        {
            levelText.text = "Level: " + gameState.currentLevel.ToString();
        }
    }

    // React Native communication methods
    private void ListenForReactNativeMessages()
    {
        // This would be implemented with a plugin
        // For example, with Unity Message system
        isReactNativeInitialized = true;
        Debug.Log("Listening for React Native messages");
    }

    private void SendScoreToReactNative()
    {
        if (isReactNativeInitialized)
        {
            // This would send the score data to React Native
            Debug.Log("Sending score to React Native: " + gameState.totalScore);
        }
    }

    private void SendProgressToReactNative()
    {
        if (isReactNativeInitialized)
        {
            // This would send the progress data to React Native
            Debug.Log("Sending progress to React Native: Level " + gameState.currentLevel);
        }
    }

    // Method to receive messages from React Native
    public void OnMessageFromReactNative(string message)
    {
        Debug.Log("Message from React Native: " + message);
        // Parse the message and take appropriate action
    }
}
