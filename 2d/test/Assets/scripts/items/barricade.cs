using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class barricade : MonoBehaviour
{
    // Start is called before the first frame update
   public float maxHealth = 200;
   public float Health = 200;

   public GameObject wood;
   public GameObject da;

   public HealthBar HealthBar;

    // Update is called once per frame
    public void SetMaxHealth(float num)
    {
        maxHealth = num;
        Health = num;
        HealthBar.SetHealth(Health, maxHealth);

    }

    void Start() {
        HealthBar.SetHealth(maxHealth, maxHealth);
    }

    public void TakeHit(float num) {
        Health -= num;
        if (Health <= 0) {
            Destroyed();
        }
        HealthBar.SetHealth(Health, maxHealth);
    }

  

    public void Destroyed() {
        Instantiate(wood, transform.position, Quaternion.identity);
        GameObject DA = Instantiate(da, transform.position, Quaternion.identity);
        Destroy(gameObject);
        Destroy(DA, 0.1f);
    }
}
