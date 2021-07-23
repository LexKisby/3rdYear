using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SceneController : MonoBehaviour
{
    
    [Header("Scene Settings")]
    public GameObject camera;
    public GameObject quad;
    public Material problem1Mat;
    public Material problem2Mat;
    public Material problem3Mat;
    public GameObject CubePrefab;
    public bool ResetCubes;
    public bool Angled = true;
    private bool _angled = true;
    public bool freeze45 = false;

    [Header("Problem 1 Settings")]
    public bool switchP1 = false;
    private bool isP1 = true;
    

    public bool forwardEnabled = true;
    public bool inverseEnabled;

    public float p1c1 = 2;
    public float p1c2 = -2;
    public float reverseC1 = 1;
    public float reverseC2 = 1;
    public bool update1 = false;
    

    [Header("Problem 2 Settings")]
    public bool switchP2 = false;
    private bool isP2 = false;

    public float amount = 0.01F;
    public bool update2 = false;
    

    [Header("Problem 3 Settings")]
    public bool switchP3 = false;
    private bool isP3 = false;

    public float p3c1 = 2;
    public float p3c2 = 2;

    public bool update3 = false;
    // Start is called before the first frame update
    void Start()
    {
        initCubes();
    }

    // Update is called once per frame
    void Update()
    {
        if (Angled == false) {
            if (_angled) {
                ResetCubes = true;
                _angled = false;
            }
        }
        if (Angled) {
            if (_angled == false) {
                ResetCubes = true;
                _angled = true;
            }
        }
        if (ResetCubes) {
            destroyCubes();
            ResetCubes = false;
            initCubes();
        }
        CheckProblem();
        CheckUpdates();


    }

    void initCubes() {
        for (int i = 0; i< 3; i ++) {
            for (int j = 0; j < 3; j++) {
                GameObject cube = Instantiate(CubePrefab, new Vector3(4*i-4, 4*j-3, 0), Quaternion.identity);
                if (Angled) {
                    cube.GetComponent<Transform>().Rotate(new Vector3(-10, 0, 0), Space.Self);
                }
                if (freeze45) {
                    cube.GetComponent<Transform>().Rotate(new Vector3(0,45, 0), Space.Self);
                    cube.GetComponent<Cube>().SetSpeed(0);
                }
            }
        }
    }

    void destroyCubes() {
        GameObject[] cubes = GameObject.FindGameObjectsWithTag("cube");
            foreach (GameObject oneObject in cubes) {
                Destroy (oneObject);
            }
    }
    void CheckUpdates() {
        if (update1) {
            problem1Mat.SetFloat("_CoEfficient1", p1c1);
            problem1Mat.SetFloat("_CoEfficient2", p1c2);
            problem1Mat.SetFloat("_CoEfficient3", reverseC1);
            problem1Mat.SetFloat("_CoEfficient4", reverseC2);
            
            problem1Mat.SetInt("_Forward", forwardEnabled ? 1 : 0);
            problem1Mat.SetInt("_Inverse", inverseEnabled ? 1 : 0);
            update1 = false;
        }
        if (update2) {
            problem2Mat.SetFloat("_amount", amount);
            update2 = false;
        }
        if (update3) {
            problem3Mat.SetFloat("_CoEfficient1", p3c1);
            problem3Mat.SetFloat("_CoEfficient2", p3c2);
            update3 = false;
        }
    }

    void CheckProblem() {
        if (switchP1) {
            if (isP1) {
                switchP1 = false;
                return;
            }
            isP1 = true;
            isP2 = false;
            isP3 = false;
            SetUp(1);
        }
        if (switchP2) {
            if (isP2) {
                switchP2 = false;
                return;
            }
            isP2 = true;
            isP1 = false;
            isP3 = false;
            SetUp(2);
        }
        if (switchP3) {
            if (isP3) {
                switchP3 = false;
                return;
            }
            isP3 = true;
            isP1 = false;
            isP2 = false;
            SetUp(3);
        }
        
    }

    void SetUp(int a) {
        if (a == 1) {
            quad.GetComponent<Renderer>().material = problem1Mat;
            camera.GetComponent<Transform>().rotation = Quaternion.identity;
            return;
        }
        if (a==2) {
            quad.GetComponent<Renderer>().material = problem2Mat;
            camera.GetComponent<Transform>().rotation = Quaternion.identity;
            return;
        }

        if (a==3) {
            quad.GetComponent<Renderer>().material = problem3Mat;
            camera.GetComponent<Transform>().Rotate(0,90,0);
            return;
        }
    }

}
