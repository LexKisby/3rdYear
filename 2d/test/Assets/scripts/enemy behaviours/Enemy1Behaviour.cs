using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Pathfinding;


public class Enemy1Behaviour : MonoBehaviour
{
    public Animator anim;

    public float Health;
    public float maxHealth = 100;
    public HealthBar HealthBar;

    public SpriteRenderer sprite;
    public GameObject deathAnim;
    public Rigidbody2D rb;
    public GameObject agent;
    public Transform target;

    public GameObject SpawnLogic;
    

    public float speed = 2f;
    public float nextWaypointDistance = 0.8f;

    Path path;
    int currentWayPoint = 0;
    bool reachedEndOfPath = false;

    Seeker seeker;

    public GameObject HealthPotion;
    public GameObject Coin;
    public GameObject Gem;

    // Start is called before the first frame update
    void Start()
    {
        Health = maxHealth;
        HealthBar.SetHealth(Health, maxHealth);

        seeker = GetComponent<Seeker>();
        agent = GameObject.Find("Agent");
        target = agent.GetComponent<Transform>();
        SpawnLogic = GameObject.Find("SpawnLogic");

        InvokeRepeating("UpdatePath", 0.5f, .5f);

    }

    public void SetHealth(float num) {
        maxHealth = num;
        Health = num;
        HealthBar.SetHealth(maxHealth, maxHealth);
    }

    void UpdatePath()
    {
        if(seeker.IsDone())
        {
        seeker.StartPath(rb.position, target.position, OnPathComplete);
    }}

    void OnPathComplete(Path p) 
    {
        if (!p.error)
        {
            path = p;
            currentWayPoint = 0;
        }
    } 

    void FixedUpdate() {
      if (path == null)
      {
          return;
      }
    if (currentWayPoint >= path.vectorPath.Count)
    {
        reachedEndOfPath = true;
        return;
    }
    else {
        reachedEndOfPath = false;
    }

    Vector2 direction = ((Vector2)path.vectorPath[currentWayPoint] - rb.position).normalized;
    speed += Random.value * 1;
    Vector2 force = direction * speed * Time.deltaTime;

    rb.AddForce(force);

    float distance = Vector2.Distance(rb.position, path.vectorPath[currentWayPoint]);

    if (distance < nextWaypointDistance) 
    {
        currentWayPoint++;
    }



    }
    // Update is called once per frame
    public void TakeHit(float damage) 
    {
        Health -= damage;
        HealthBar.SetHealth(Health, maxHealth);
        if (Health <= 0) {
            GameObject death = Instantiate(deathAnim, transform.position, Quaternion.identity);
            SpawnLogic.GetComponent<SpawnLogic>().KilledOne();
            Destroy(death, 0.4f);
            sprite.color = new Color(0,0,0,1);
            Destroy(gameObject, 0.1f);
            SpawnItem();
        }
    }
    public void Knockback(Vector2 direction, float force) {
        direction.Normalize();
        anim.SetBool("knockback", true);
        Invoke("disable", 0.1f);
        rb.AddForce(force * direction);
    }
    void disable() {
        anim.SetBool("knockback", false);
    }

    void SpawnItem()
    {
        float x = Random.value;
        if (x < 0.04f) {
            GameObject Potion = Instantiate(HealthPotion, transform.position, Quaternion.identity);
            return;
        }
        if (x < 0.5f) {
            GameObject coin = Instantiate(Coin, transform.position, Quaternion.identity);
            return;
        }
        if (x > 0.93) {
            GameObject gem = Instantiate(Gem, transform.position, Quaternion.identity);
            return;
        }
        
    }
    

    void OnCollisionEnter2D(Collision2D collInfo)
    {
        Collider2D hitInfo = collInfo.collider;
        if (hitInfo.name == "Agent")
        {
            AgentController agent = hitInfo.GetComponent<AgentController>();
            agent.TakeHit(2f);
            agent.Knockback(hitInfo.GetComponent<Transform>().position - transform.position, 400f);
            Knockback(transform.position - hitInfo.GetComponent<Transform>().position, 400f);            
        }
        if (hitInfo.tag == "barricade")
        {
            barricade barricade = hitInfo.GetComponent<barricade>();
            barricade.TakeHit(3f);
            Knockback(transform.position - hitInfo.GetComponent<Transform>().position, 400f);
        }
        if (hitInfo.tag == "turret") {
            Debug.Log("turret hit");
            GameObject child = hitInfo.gameObject;
            GameObject par = child.transform.parent.gameObject;
            turret t = par.GetComponent<turret>();
            t.TakeHit(3f);
            Knockback(transform.position -  hitInfo.GetComponent<Transform>().position, 400f);
        }
    }
}
