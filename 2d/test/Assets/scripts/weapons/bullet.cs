using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class bullet : MonoBehaviour
{
    
    public GameObject ImpactPrefab;
    public Rigidbody2D rb;
    public float damage = 5f;


    void OnTriggerEnter2D(Collider2D hitInfo) {
        if (hitInfo.tag == "torch") {
            return;
        }
        if (hitInfo.tag == "turret") {
            return;
        }
        if (hitInfo.name == "bullet1(Clone)") {
            return;
        }
        if (hitInfo.tag == "building") {
            return;
        }
        if (hitInfo.name == "coin(Clone)") {
            return;
        }
        if (hitInfo.name == "wood(Clone)") {
            return;
        }
        if (hitInfo.name == "Health Potion(Clone)") {
            return;
        }
        if (hitInfo.name == "Gem(Clone)") {
            return;
        }
        
        if (hitInfo.name != "Agent") {
            if (hitInfo.tag == "barricade") {
                barricade barricade = hitInfo.GetComponent<barricade>();
                barricade.TakeHit(damage);
                Destroy(gameObject);
                GameObject impact2 = Instantiate(ImpactPrefab, transform.position, Quaternion.identity);
                Destroy(impact2, 0.4f);
                return;
            }
            Enemy1Behaviour enemy = hitInfo.GetComponent<Enemy1Behaviour>();
            if (enemy != null) {
            enemy.TakeHit(damage);
            enemy.Knockback(rb.velocity, 300);
            }
            Destroy(gameObject);
            GameObject impact = Instantiate(ImpactPrefab, transform.position, Quaternion.identity);
            Destroy(impact, 0.4f);
        }
        
        
    }

    public void SetDamage(float value) {
        damage = value;
    }
}
