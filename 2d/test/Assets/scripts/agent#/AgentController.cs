using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AgentController : MonoBehaviour
{
    GameObject logic;

    public GameObject buy;
    public GameObject pickup;

    public bool power = false;
    public bool lab = false;
    public bool factory = false;
    public bool gunsmith = false;
    public bool carpenter = false;
    public int atGate = 0;
    public float buildingDelay = 0f;

    public bool PowerOn = false;
    public bool hasOrb = false;

    public GameObject researchLab;

    public bool researching;
    
    public Animator topAnimator;
    public Animator bottomAnimator;
    public GameObject top;
    public GameObject bottom;

    public Animator Chun;
    public Animator Cten;
    public Animator Cone;

    public Animator Ghun;
    public Animator Gten;
    public Animator Gone;

    public Animator Phun;
    public Animator Pten;
    public Animator Pone;

    public Animator Whun;
    public Animator Wten;
    public Animator Wone;

    public Animator Thun;
    public Animator Tten;
    public Animator Tone;

    public Animator Bhun;
    public Animator Bten;
    public Animator Bone;

    public Animator TUhun;
    public Animator TUten;
    public Animator TUone;

    public GameObject DeathAnim;
    public GameObject GraveAnim;
    public GameObject GraveObj;

    public GameObject torch;
    public GameObject barricade;
    public GameObject turret;


    public GameObject crossHair;
    public GameObject bullet1Prefab;
    public Vector3 mousePos;
    public Rigidbody2D rb;
    public float delay;
    public bool isShooting;

    public float Health = 10f;
    public float maxHealth = 10f;
    public AgentHealth AgentHealth;
    public bool isDead = false;
    float dethTimer = 0.6f;

    public float speed = 3f;
    public float potionStrength = 2f;
    public float barricadeStrength = 50;
    public int autoLvl = 0;
    public bool Auto = false;
    public int turretLvl = 0;
    public bool isAuto;
     int shotDelay = 40;

    public float bulletStrength = 5;
    public int ROF = 0;

    Vector3 movement;
    Vector3 aim;
    Vector2 shootingDirection;
    bool isAiming;

    public int HealthPotions = 0;
    
    public int Gems = 0;
    public int Coins = 0;
    public int wood = 0;

    public int torches = 0;
    public int barricades = 0;
    public int turrets = 0;

    bool immortal = false;

    
    public int GetAutoLvl() {
        return autoLvl;
    }

    public int GetTurretLvl() {
        return turretLvl;
    }
    // Start is called before the first frame update
    void Start()
    {
        hasOrb = false;
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
        Health = maxHealth;
        AgentHealth.SetHealth(maxHealth, maxHealth);
        logic = GameObject.Find("SpawnLogic");
        potionStrength = 2.0f;
        speed = 3f;
        barricadeStrength = 50f;
        bulletStrength = 5f;
        bullet1Prefab.GetComponent<bullet>().SetDamage(bulletStrength);
    }

    // Update is called once per frame
    void Update()
    {
        
        ProcessInputs();

        if (isDead)
        {
            dethTimer -= Time.deltaTime;
            if (dethTimer < 0) {
            GameObject g = Instantiate(GraveObj, transform.position, Quaternion.identity);
            dethTimer = 100f;
            }
            return;
        }
        NextToBuilding();
        Gates();
        AimAndShoot();

        Animate();
        Move();

        PlaceItem();
    }
    void PlaceItem(){
        if (Input.GetKeyDown(KeyCode.E))
        {
            if (torches >= 1){
            Instantiate(torch, transform.position, Quaternion.identity);
            torches -= 1;
            Thun.SetInteger("hundreds", (torches/100) % 10);
            Tten.SetInteger("tens", (torches/10) % 10);
            Tone.SetInteger("ones", torches % 10);
        }}
        if (Input.GetKeyDown(KeyCode.R))
        {
           if (barricades >= 1) {
            GameObject b = Instantiate(barricade, transform.position + (Vector3)shootingDirection.normalized * 0.4f, Quaternion.identity);
            b.transform.Rotate(0.0f, 0.0f, Mathf.Atan2(shootingDirection.y, shootingDirection.x) * Mathf.Rad2Deg);
            barricade bar = b.GetComponent<barricade>();
            bar.SetMaxHealth(barricadeStrength);
            barricades -= 1;
            Bhun.SetInteger("hundreds", (barricades/100) % 10);
            Bten.SetInteger("tens", (barricades/10) % 10);
            Bone.SetInteger("ones", barricades % 10);
        }}
        if (Input.GetKeyDown(KeyCode.T)) {
            if (turrets >= 1) {
            GameObject t = Instantiate(turret, transform.position + (Vector3)shootingDirection.normalized * 0.4f, Quaternion.identity);
            t.transform.Rotate(0.0f, 0.0f, Mathf.Atan2(shootingDirection.y, shootingDirection.x) * Mathf.Rad2Deg);
            turret tur = t.GetComponent<turret>();
            tur.UpdateStats(autoLvl, turretLvl);
            turrets -= 1;
            TUhun.SetInteger("hundreds", (turrets/100) % 10);
        TUten.SetInteger("tens", (turrets/10) % 10);
        TUone.SetInteger("ones", turrets% 10);
            }
        }
    }
    public void Heal(float strength) {
        if (HealthPotions >= 1) {
                HealthPotions -= 1;
                Phun.SetInteger("hundreds", (HealthPotions/100) % 10);
                Pten.SetInteger("tens", (HealthPotions/10) % 10);
                Pone.SetInteger("ones", HealthPotions% 10);
                Debug.Log(strength);
            Health += strength;
            Debug.Log(Health);
            if (Health > maxHealth) {
                Health = maxHealth;
            }
            AgentHealth.SetHealth(Health, maxHealth);
        } else {
            //Instantiate error message
        }
        
    }

    public void PickUpHealthPotion() {
        GameObject p = Instantiate(pickup, transform.position, Quaternion.identity);
        Destroy(p, 0.8f);
        HealthPotions += 1;
        Phun.SetInteger("hundreds", (HealthPotions/100) % 10);
        Pten.SetInteger("tens", (HealthPotions/10) % 10);
        Pone.SetInteger("ones", HealthPotions% 10);
    }

    public void PickUpWood() {
        GameObject p = Instantiate(pickup, transform.position, Quaternion.identity);
        Destroy(p, 0.8f);
        wood += 1;
        Whun.SetInteger("hundreds", (wood/100) % 10);
        Wten.SetInteger("tens", (wood/10) % 10);
        Wone.SetInteger("ones", wood % 10); 
    }

    public void PickUpGem()
    {
        GameObject p = Instantiate(pickup, transform.position, Quaternion.identity);
        Destroy(p, 0.8f);
        Gems += 1;
        Ghun.SetInteger("hundreds", (Gems/100) % 10);
        Gten.SetInteger("tens", (Gems/10) % 10);
        Gone.SetInteger("ones", Gems % 10);
    }

    public void PickUpCoin() {
        Coins += 1;
        GameObject p = Instantiate(pickup, transform.position, Quaternion.identity);
        Destroy(p, 0.8f);
        Chun.SetInteger("hundreds", (Coins/100) % 10);
        Cten.SetInteger("tens", (Coins/10) % 10);
        Cone.SetInteger("ones", Coins % 10);
    }

    public void TakeHit(float damage) {
        if (!isDead) {
        Health -= damage;
        if (Health < 0.001f) {
            isDead = true;
            AgentHealth.SetHealth(0f, maxHealth);
            Health = 0;
            if (!immortal) {
            top.SetActive(false);
            bottom.SetActive(false);
            SpawnLogic script = logic.GetComponent<SpawnLogic>();
            script.GameOver();
            rb.bodyType = RigidbodyType2D.Static;
            GameObject ded = Instantiate(DeathAnim, transform.position, Quaternion.identity);
            GameObject grave = Instantiate(GraveAnim, transform.position, Quaternion.identity);
            
            Destroy(ded, 0.3f);
            Destroy(grave, 0.6f);
            }
        } 
        else {
            AgentHealth.SetHealth(Health, maxHealth);
        } 
        }
    }

    public void Knockback(Vector2 direction, float force){
        if (!isDead) {
        direction.Normalize();

        rb.AddForce(force * direction);
        }
    }

    void ProcessInputs() {
        movement = new Vector3(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical"), 0.0f);
    
        mousePos = new Vector3(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y"), 0.0f);
        aim = aim + mousePos;
        if (aim.magnitude > 1.0f) {
            aim.Normalize();
        }
        isShooting = Input.GetButtonDown("Fire1");
        isAuto = Input.GetButton("Fire1");
        if (movement.magnitude > 1.0f) {
            movement.Normalize();
        }

        if (Input.GetKeyDown(KeyCode.H)) {
            
            Heal(potionStrength);
            
        }
        
    }

    void Animate() {
        bottomAnimator.SetFloat("Horizontal", movement.x);
        bottomAnimator.SetFloat("Magnitude", movement.magnitude);
        topAnimator.SetFloat("MoveHorizontal", movement.x);
        topAnimator.SetFloat("MoveMagnitude", movement.magnitude);

        topAnimator.SetFloat("AimMagnitude", aim.magnitude);
        topAnimator.SetFloat("AimHorizontal", shootingDirection.x);
        topAnimator.SetFloat("AimVertical", shootingDirection.y);
    }

    void Move() {
        //transform.position = transform.position + 2*movement * Time.deltaTime;
        rb.velocity = new Vector2(speed*movement.x, speed*movement.y);

    }

    private void AimAndShoot(){
        topAnimator.SetBool("Shoot", false);
        shootingDirection = new Vector2(aim.x, aim.y);

        if (mousePos.magnitude > 0.0f) {
            
            crossHair.transform.localPosition = 0.6f * aim;
            crossHair.SetActive(true);
            topAnimator.SetBool("Aim", true);
        
            delay = Time.time;

            
            
        } 
        else 
        {
            if (Time.time - delay > 0.3f)
            {
            crossHair.SetActive(false);
            topAnimator.SetBool("Aim", false);
                }
            }
        if (isShooting) {
            isShooting = true;
            topAnimator.SetBool("Shoot", true);
            shootingDirection.Normalize();
            GameObject bullet = Instantiate(bullet1Prefab, transform.position + 0.2f * new Vector3(shootingDirection.x, shootingDirection.y, 0.0f), Quaternion.identity);
            
            bullet.GetComponent<Rigidbody2D>().velocity = 5.0f * shootingDirection;
            bullet.transform.Rotate(0.0f, 0.0f, Mathf.Atan2(shootingDirection.y, shootingDirection.x) * Mathf.Rad2Deg);
            Destroy(bullet, 2.0f);
            } else {
        
        if (isAuto) {
            if (Auto == true) {
                shotDelay -= 1;
                if (shotDelay < 0) {
                    shotDelay = 0;
                }
                if (shotDelay == 0) {
                    shotDelay = 40 - 5 * ROF;
                topAnimator.SetBool("Shoot", true);
                shootingDirection.Normalize();
                GameObject bullet = Instantiate(bullet1Prefab, transform.position + 0.2f * new Vector3(shootingDirection.x, shootingDirection.y, 0.0f) + 0.2f * new Vector3(Random.value, Random.value, 0), Quaternion.identity);
                
                bullet.GetComponent<Rigidbody2D>().velocity = 5.0f * shootingDirection;
                bullet.transform.Rotate(0.0f, 0.0f, Mathf.Atan2(shootingDirection.y, shootingDirection.x) * Mathf.Rad2Deg);
                Destroy(bullet, 2.0f);
                }
        }
        }
        
        
         }   
        
    }
    public void AtGate(int g) {
        Debug.Log("at gate");
        Debug.Log(g);
        atGate = g;
    }

    public void LeftGate() {
        atGate = 0;
    }

    public void GotOrb() {
        hasOrb = true;
    }

    public void NextToLab(){
        
        lab = true;
    }

    public void NextToFactory(){
        
        factory = true;
    }

    public void NextToGunsmith(){
        
        gunsmith = true;
    }

    public void NextToPower() {
       
        power = true;
    }

    public void NextToCarpenter() {
       
        carpenter = true;
    }

    public void LeftBuilding() {
        lab = false;
        factory = false;
        gunsmith = false;
        power = false;
        carpenter = false;
    }

    void NextToBuilding() {
            if (power) {
                if (Input.GetKeyDown(KeyCode.Space)) {
                    if(hasOrb) {
                        PowerOn = true;
                        GameObject p = GameObject.Find("Power");
                        building b = p.GetComponent<building>();
                        b.PowerOn();
                        GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                    }
                }
                return;
            }

            if (lab) {
                if (researching) {
                    return;
                }
                if (Input.GetKeyDown(KeyCode.Alpha1)) {
                    if (Coins >= 10) {
                    Coins -= 10;
                    potionStrength += 2;
                    researching = true;
                    researchLab.GetComponent<building>().Researching();
                    Invoke("EndResearch", 10f);
                    GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                }
                }
                if (Input.GetKeyDown(KeyCode.Alpha2)) {
                    if (Coins >= 10) {
                    Coins -= 10;
                    barricadeStrength += 50;
                    researching = true;
                    researchLab.GetComponent<building>().Researching();
                    Invoke("EndResearch", 10f);
                    GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                }

                }
                if (Input.GetKeyDown(KeyCode.Alpha3)) {
                    //upgrade character speed
                    if (Coins >= 10) {
                    Coins -= 10;
                    speed += 0.4f;
                    researching = true;
                    researchLab.GetComponent<building>().Researching();
                    Invoke("EndResearch", 10f);
                    GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                }
                }
                if (Input.GetKeyDown(KeyCode.Alpha4)) {
                    //Upgrade character health
                    if (Coins >= 10) {
                    Coins -= 10;
                    maxHealth += 5;
                    Health += 5;
                    AgentHealth.SetHealth(Health, maxHealth);
                    researching = true;
                    researchLab.GetComponent<building>().Researching();
                    Invoke("EndResearch", 10f);
                    GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                }}
                if (Input.GetKeyDown(KeyCode.Alpha5)) {
                    //Upgrade rof / unlock auto
                    if (Gems >= 2 * (autoLvl + 1)) {
                    Auto = true;
                    Gems -= 2 * (autoLvl + 1);
                    autoLvl += 1;
                    researching = true;
                    researchLab.GetComponent<building>().Researching();
                    Invoke("EndResearch", 30f);
                    GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                }}
                if (Input.GetKeyDown(KeyCode.Alpha6)) {
                    //unlock turrets / upgrade health
                    if (Gems >= 2 * (turretLvl + 1)) {
                    Gems -= 2 * (turretLvl + 1);
                    turretLvl += 1;
                    researching = true;
                    researchLab.GetComponent<building>().Researching();
                    Invoke("EndResearch", 30f);
                    GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                }}
                Chun.SetInteger("hundreds", (Coins/100) % 10);
                Cten.SetInteger("tens", (Coins/10) % 10);
                Cone.SetInteger("ones", Coins % 10);
                Ghun.SetInteger("hundreds", (Gems/100) % 10);
                Gten.SetInteger("tens", (Gems/10) % 10);
                Gone.SetInteger("ones", Gems% 10);
                return;
            }
            if (factory) {
                if (Input.GetKeyDown(KeyCode.Space)) {
                    if (turretLvl == 0) {
                        return;
                    }
                    if (Coins >= 15) {
                        Coins -= 15;
                        turrets += 1;
                        TUhun.SetInteger("hundreds", (turrets/100) % 10);
                        TUten.SetInteger("tens", (turrets/10) % 10);
                        TUone.SetInteger("ones", turrets% 10);
                        Chun.SetInteger("hundreds", (Coins/100) % 10);
                        Cten.SetInteger("tens", (Coins/10) % 10);
                        Cone.SetInteger("ones", Coins% 10);
                        GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                    }
                }
                return;
            }
            if (gunsmith) {
                if (Input.GetKeyDown(KeyCode.Alpha1)) {
                    if (Coins >= 10) {
                    Coins -= 10;
                    bulletStrength += 5;
                    bullet b = bullet1Prefab.GetComponent<bullet>();
                    b.SetDamage(bulletStrength);
                    Chun.SetInteger("hundreds", (Coins/100) % 10);
                    Cten.SetInteger("tens", (Coins/10) % 10);
                    Cone.SetInteger("ones", Coins % 10);
                    GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                    
                } }
                if (Input.GetKeyDown(KeyCode.Alpha2)) {
                    //Upgrade to auto / increase rof
                    if (autoLvl > ROF) {
                        if (Coins >= 10) {
                            Coins -= 10;
                            ROF += 1;
                            Chun.SetInteger("hundreds", (Coins/100) % 10);
                            Cten.SetInteger("tens", (Coins/10) % 10);
                            Cone.SetInteger("ones", Coins% 10);
                            GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                   
                    
                }
                    }
                    }
                return;
            }
            
            if (carpenter) {
                if (Input.GetKeyDown(KeyCode.Alpha1)) {
                    if (wood >= 1) {
                    torches += 1;
                    wood -= 1;
                    Whun.SetInteger("hundreds", (wood/100) % 10);
                    Wten.SetInteger("tens", (wood/10) % 10);
                    Wone.SetInteger("ones", wood % 10);
                    Thun.SetInteger("hundreds", (torches/100) % 10);
                    Tten.SetInteger("tens", (torches/10) % 10);
                    Tone.SetInteger("ones", torches % 10);
                    GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                    }
                }
                if (Input.GetKeyDown(KeyCode.Alpha2)) {
                    if (wood >= 3) {
                        barricades += 1;
                        wood -= 3;
                         Whun.SetInteger("hundreds", (wood/100) % 10);
                    Wten.SetInteger("tens", (wood/10) % 10);
                    Wone.SetInteger("ones", wood % 10);
                    Bhun.SetInteger("hundreds", (barricades/100) % 10);
                    Bten.SetInteger("tens", (barricades/10) % 10);
                    Bone.SetInteger("ones", barricades % 10);
                    GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                    }
                }
                return;
            }
        }

        void EndResearch() {
            researching = false;
            researchLab.GetComponent<building>().ResearchDone();
        }

        void Gates() {
            if (atGate == 0) {
                return;
            }
            if (PowerOn == false) {
                return;
            }
            if (Coins >= 10) {
                if (Input.GetKeyDown(KeyCode.Space)) {
                    if (atGate == 1) {
                        GameObject g = GameObject.Find("Gate1");
                        g.GetComponent<gate>().Open();
                        SpawnLogic script = logic.GetComponent<SpawnLogic>();
                        script.GateOpen(1);
                        Coins -= 10;
                        GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                    }
                    if (atGate == 2) {
                        GameObject g = GameObject.Find("Gate2");
                        g.GetComponent<gate>().Open();
                         SpawnLogic script = logic.GetComponent<SpawnLogic>();
                        script.GateOpen(2);
                        Coins -= 10;
                        GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                    }
                    if (atGate == 3) {
                        GameObject g = GameObject.Find("Gate3");
                        g.GetComponent<gate>().Open();
                         SpawnLogic script = logic.GetComponent<SpawnLogic>();
                        script.GateOpen(3);
                        Coins -= 10;
                        GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                    }
                    if (atGate == 4) {
                        GameObject g = GameObject.Find("Gate4");
                        g.GetComponent<gate>().Open();
                         SpawnLogic script = logic.GetComponent<SpawnLogic>();
                        script.GateOpen(4);
                        Coins -= 10;
                        GameObject Buy = Instantiate(buy, transform.position, Quaternion.identity);
                        Destroy(Buy, 0.8f);
                        
                    }
                    Chun.SetInteger("hundreds", (Coins/100) % 10);
                            Cten.SetInteger("tens", (Coins/10) % 10);
                            Cone.SetInteger("ones", Coins% 10);
                }
            }
        }
    
}
