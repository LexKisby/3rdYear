using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class turret : MonoBehaviour
{
    public GameObject bullet;
    private GameObject player;
    private AgentController playerData;
    public HealthBar HP;
    public Transform spriteRot;
    public GameObject DeathAnim;

    public int ROF;
    public int turretLvl;

    public float Health;
    public float MaxHealth;

    public bool hasTarget;
    public List<GameObject> Target;
    int shotDelay = 40;


    public void TakeHit(float damage) {
        Health -= damage;
        if (Health < 0) {
            GameObject d = Instantiate(DeathAnim, transform.position, Quaternion.identity);
            Destroy(d, 0.4f);
            Destroy(gameObject);
        }
        HP.SetHealth(Health, MaxHealth);
    }
    
    // Start is called before the first frame update
    void Start()
    {
        player = GameObject.Find("Agent");
        playerData = player.GetComponent<AgentController>();
        Health = 10;
        MaxHealth = 10;
        HP.SetHealth(Health, MaxHealth);
        ROF = 1;
        Target = new List<GameObject>();
        
    }
    public void UpdateStats(int a, int b) {
        ROF = a;
        turretLvl = b;

        MaxHealth = 10 * turretLvl * turretLvl;
        Health = MaxHealth;
        HP.SetHealth(Health, MaxHealth);
    }

    void OnTriggerEnter2D(Collider2D hitInfo) {
        
        if (hitInfo.tag == "enemy") {
            hasTarget = true;
            Target.Add(hitInfo.gameObject);
        }
    }

    void OnTriggerExit2D(Collider2D hitInfo) {
        Target.Remove(hitInfo.gameObject);
        if (Target.Count == 0) {
            hasTarget = false;
        }
    }

    // Update is called once per frame
    void Update()
    {
        //if has target, shoots
        if (!hasTarget) {
            return;
        }
        if (Target.Count == 0) {
            hasTarget = false;
            return;
        }
        if (Target[0] == null) {
            Target.Remove(Target[0]);
            return;
        }
        Vector2 shootingDirection = (Vector2)(Target[0].GetComponent<Transform>().position - transform.position);
        shootingDirection.Normalize();
        spriteRot.transform.eulerAngles = new Vector3(0f, 0f, Mathf.Atan2(shootingDirection.y, shootingDirection.x) * Mathf.Rad2Deg - 90);
        shotDelay -= 1;
                if (shotDelay < 0) {
                    shotDelay = 0;
                }
                if (shotDelay == 0) {
                    shotDelay = 40 - 5 * ROF;
                
                GameObject b = Instantiate(bullet, transform.position + 0.4f * new Vector3(shootingDirection.x, shootingDirection.y, 0.0f) + 0.2f * new Vector3(Random.value, Random.value, 0), Quaternion.identity);
                
                b.GetComponent<Rigidbody2D>().velocity = 5.0f * shootingDirection;
                b.transform.Rotate(0.0f, 0.0f, Mathf.Atan2(shootingDirection.y, shootingDirection.x) * Mathf.Rad2Deg);
                
                Destroy(b, 2.0f);
                }
        
    }
}
