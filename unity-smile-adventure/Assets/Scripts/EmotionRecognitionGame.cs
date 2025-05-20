using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class EmotionRecognitionGame : MonoBehaviour
{
    [Header("Game Settings")]
    [SerializeField] private float gameDuration = 60f;
    [SerializeField] private int pointsPerCorrectAnswer = 10;
    [SerializeField] private int penaltyPerWrongAnswer = 5;
    
    [Header("UI References")]
    [SerializeField] private Image emotionImage;
    [SerializeField] private Button[] emotionButtons;
    [SerializeField] private Slider timerSlider;
    [SerializeField] private GameObject gamePanel;
    [SerializeField] private GameObject resultPanel;
    [SerializeField] private Text resultText;
    
    [Header("Emotions")]
    [SerializeField] private List<EmotionData> emotionsList = new List<EmotionData>();
    
    // Game state variables
    private float remainingTime;
    private int score;
    private int correctAnswers;
    private int wrongAnswers;
    private EmotionData currentEmotion;
    private bool isGameActive = false;
    
    [System.Serializable]
    public class EmotionData
    {
        public string emotionName;
        public Sprite emotionSprite;
        public Color buttonColor = Color.white;
        [TextArea] public string description;
    }
    
    private void Start()
    {
        // Set up emotion buttons
        SetupEmotionButtons();
        
        // Reset and initialize game panel
        gamePanel.SetActive(false);
        resultPanel.SetActive(false);
    }
    
    private void SetupEmotionButtons()
    {
        // Make sure we have enough buttons for emotions
        if (emotionButtons.Length < emotionsList.Count)
        {
            Debug.LogError("Not enough emotion buttons for all emotions!");
            return;
        }
        
        // Set up each button with emotion name and color
        for (int i = 0; i < emotionsList.Count; i++)
        {
            EmotionData emotion = emotionsList[i];
            Button button = emotionButtons[i];
            
            // Set button text
            Text buttonText = button.GetComponentInChildren<Text>();
            if (buttonText != null)
            {
                buttonText.text = emotion.emotionName;
            }
            
            // Set button color
            ColorBlock colors = button.colors;
            colors.normalColor = emotion.buttonColor;
            button.colors = colors;
            
            // Set button click action
            int index = i; // Need to use a local variable for closure
            button.onClick.RemoveAllListeners();
            button.onClick.AddListener(() => OnEmotionSelected(index));
            
            // Make sure button is active
            button.gameObject.SetActive(true);
        }
        
        // Hide any unused buttons
        for (int i = emotionsList.Count; i < emotionButtons.Length; i++)
        {
            emotionButtons[i].gameObject.SetActive(false);
        }
    }
    
    public void StartGame()
    {
        // Reset game state
        score = 0;
        correctAnswers = 0;
        wrongAnswers = 0;
        remainingTime = gameDuration;
        
        // Show game panel
        gamePanel.SetActive(true);
        resultPanel.SetActive(false);
        
        // Start the game
        isGameActive = true;
        
        // Show first emotion
        ShowRandomEmotion();
        
        // Start timer
        StartCoroutine(GameTimer());
    }
    
    private IEnumerator GameTimer()
    {
        while (remainingTime > 0 && isGameActive)
        {
            remainingTime -= Time.deltaTime;
            
            // Update timer UI
            if (timerSlider != null)
            {
                timerSlider.value = remainingTime / gameDuration;
            }
            
            yield return null;
        }
        
        if (isGameActive)
        {
            EndGame();
        }
    }
    
    private void ShowRandomEmotion()
    {
        // Select a random emotion
        int randomIndex = Random.Range(0, emotionsList.Count);
        currentEmotion = emotionsList[randomIndex];
        
        // Update UI
        if (emotionImage != null && currentEmotion.emotionSprite != null)
        {
            emotionImage.sprite = currentEmotion.emotionSprite;
            emotionImage.preserveAspect = true;
        }
    }
    
    public void OnEmotionSelected(int emotionIndex)
    {
        if (!isGameActive) return;
        
        EmotionData selectedEmotion = emotionsList[emotionIndex];
        bool isCorrect = selectedEmotion.emotionName == currentEmotion.emotionName;
        
        if (isCorrect)
        {
            // Correct answer
            score += pointsPerCorrectAnswer;
            correctAnswers++;
            
            // Play success sound
            if (GameManager.Instance != null)
            {
                AudioSource audioSource = GetComponent<AudioSource>();
                if (audioSource != null && GameManager.Instance.successSound != null)
                {
                    audioSource.PlayOneShot(GameManager.Instance.successSound);
                }
            }
        }
        else
        {
            // Wrong answer
            score -= penaltyPerWrongAnswer;
            wrongAnswers++;
            
            // Play fail sound
            if (GameManager.Instance != null)
            {
                AudioSource audioSource = GetComponent<AudioSource>();
                if (audioSource != null && GameManager.Instance.failSound != null)
                {
                    audioSource.PlayOneShot(GameManager.Instance.failSound);
                }
            }
        }
        
        // Update score in GameManager
        if (GameManager.Instance != null)
        {
            GameManager.Instance.AddScore(isCorrect ? pointsPerCorrectAnswer : -penaltyPerWrongAnswer);
        }
        
        // Show next emotion
        ShowRandomEmotion();
    }
    
    private void EndGame()
    {
        isGameActive = false;
        
        // Show result panel
        gamePanel.SetActive(false);
        resultPanel.SetActive(true);
        
        // Update result text
        if (resultText != null)
        {
            resultText.text = $"Punteggio finale: {score}\n" +
                             $"Risposte corrette: {correctAnswers}\n" +
                             $"Risposte sbagliate: {wrongAnswers}";
        }
        
        // Notify GameManager
        if (GameManager.Instance != null)
        {
            GameManager.Instance.CompleteLevel();
        }
    }
    
    public void RestartGame()
    {
        StartGame();
    }
    
    public void QuitGame()
    {
        // Return to main menu or previous screen
        gamePanel.SetActive(false);
        resultPanel.SetActive(false);
        isGameActive = false;
    }
}
