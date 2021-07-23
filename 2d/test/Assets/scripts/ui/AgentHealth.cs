using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class AgentHealth : MonoBehaviour
{
    public Slider Slider;
    public Gradient grad;

    // Start is called before the first frame update
    public void SetHealth(float health, float maxHealth) {
        Slider.maxValue = maxHealth;
        Slider.value = health;
        

        Slider.fillRect.GetComponentInChildren<Image>().color = grad.Evaluate(health/maxHealth);
    }

    // Update is called once per frame
   
}
