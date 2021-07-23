using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class HealthBar : MonoBehaviour
{

    public Slider Slider;
    public Gradient grad;
    

    public void SetHealth(float health, float maxHealth) {
        Slider.gameObject.SetActive(health != maxHealth);
        
        Slider.maxValue = maxHealth;
        Slider.value = health;

        Slider.fillRect.GetComponentInChildren<Image>().color = grad.Evaluate(health/maxHealth);
    }

    // Update is called once per frame
    
}
