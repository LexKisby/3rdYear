using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class SpawnLogic : MonoBehaviour
{
    public Animator hundreds;
    public Animator tens;
    public Animator ones;
    public int Round;
    public int RemainingAlive;
    public int RemainingToSpawn;
    public int Total;
    public float RoundTimer;
    public float RoundBreak;
    public int Gates;
    public bool brain;
    public bool lung_left;
    public bool lung_right;
    public bool intestine;
    
    public GameObject Enemy1;

    private GameObject agent;
    private Transform agentPos;


    private GameObject[] Spawns;
    private GameObject s1;
    private GameObject s2;
    private GameObject s3;
    private GameObject s4;
    private GameObject s5;
    private GameObject s6;
    private GameObject s7;
    public GameObject Orb;
    private GameObject[] OrbSpawns;
    private GameObject[] enemies;
    private int CurrentSpawner;
    
    // Start is called before the first frame update
    void Start()
    {
        lung_right = false;
        lung_left = false;
        brain = false;
        intestine = false;

        Round = 0;
        RemainingAlive = 10;
        RemainingToSpawn = 10;
        Total = 0;
        RoundTimer = 30f;
        RoundBreak = 15f;
        CurrentSpawner = 0;
        agent = GameObject.Find("Agent");
        agentPos = agent.GetComponent<Transform>();

        
        s1 = GameObject.Find("spawnPt");
        s2 = GameObject.Find("spawnPt (1)");
        s3 = GameObject.Find("spawnPt (2)");
        s4 = GameObject.Find("spawnPt (3)");
        s5 = GameObject.Find("spawnPt (4)");
        s6 = GameObject.Find("spawnPt (5)");
        s7 = GameObject.Find("spawnPt (6)");
        Spawns = new GameObject[7];
        Spawns[0] = s1;
        Spawns[1] = s2;
        Spawns[2] = s3;
        Spawns[3] = s4;
        Spawns[4] = s5;
        Spawns[5] = s6;
        Spawns[6] = s7;
        
        OrbSpawns = GameObject.FindGameObjectsWithTag("orbspawner");

        if (Random.value > 0.67f) {
            Instantiate(Orb, OrbSpawns[0].GetComponent<Transform>().position, Quaternion.identity);
        }
        else {
            if (Random.value > 0.5f) {
                Instantiate(Orb, OrbSpawns[1].GetComponent<Transform>().position, Quaternion.identity);
            } else {
                Instantiate(Orb, OrbSpawns[2].GetComponent<Transform>().position, Quaternion.identity);
            }
        }

        NextRound();
    }

    public void GateOpen(int num) {
        if (num == 1) {
            lung_left = true;
            return;
        }
        if (num == 2) {
            brain = true;
            return;
        }
        if (num == 3) {
            lung_right = true;
            return;
        }
        if (num == 4) {
            intestine = true;
        }
    }

    // Update is called once per frame
    void FixedUpdate()
    {
         if (CurrentSpawner > 6){
            CurrentSpawner = 0;
        }
        if (RemainingAlive <= 0)
        {
            enemies = GameObject.FindGameObjectsWithTag("enemy");
            if (enemies.Length != 0) {
                return;
            }
            if (RoundBreak > 0.0f){
                RoundBreak -= Time.deltaTime;
                return;
            }
            RoundBreak = 15f;
            NextRound();
            return;
        }
        if (RemainingToSpawn == 0)
        {
            return;
        }
        if (!intestine && (CurrentSpawner ==  2| CurrentSpawner == 6)) {
            CurrentSpawner += 1;
            return;
        }
        if (!brain && CurrentSpawner == 3) {
            CurrentSpawner += 1;
            return;
        }

        if (!lung_left && CurrentSpawner == 5) {
            CurrentSpawner+=1;
            return;
        }
        if (!lung_right && CurrentSpawner == 4) {
            CurrentSpawner += 1;
            return;
        }
        
        float distance = (Spawns[CurrentSpawner].GetComponent<Transform>().position - agentPos.position).magnitude;
        if (distance > 10f)
        {
        



            GameObject baddie = Instantiate(Enemy1, Spawns[CurrentSpawner].GetComponent<Transform>().position, Quaternion.identity);
            RemainingToSpawn -= 1;
            Enemy1Behaviour script = baddie.GetComponent<Enemy1Behaviour>();
            script.SetHealth(Round * 5 + 5);

        }
        CurrentSpawner+=1;
       
    }

    void NextRound()
    {
        Round += 1;
        UpdateRoundCounter();
        
        RemainingAlive = 5 * Round + 5;
        
        
        RemainingToSpawn = RemainingAlive;
        RoundTimer = 0f;
    }

    public void KilledOne() {
        RemainingAlive -= 1;
        Total += 1;
    }

    void UpdateRoundCounter(){
        hundreds.SetInteger("hundreds", (Round/100) % 10);
        tens.SetInteger("tens", (Round/10) % 10);
        ones.SetInteger("ones", Round % 10);
    }

    public void GameOver() {
        Invoke("ToMenu", 2f);
    }

    void Restart() {
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }

    void ToMenu() {
        SceneManager.LoadScene("StartScene");
    }



}
