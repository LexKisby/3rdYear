using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class building : MonoBehaviour
{

    public int type;
    public Animator anim;
    public Animator sliderAnim1;
    public Animator sliderAnim2;

    void OnTriggerEnter2D(Collider2D hitInfo) {
        if (hitInfo.name == "Agent") {
            Debug.Log("hello");
            AgentController script = hitInfo.GetComponent<AgentController>();
            if (type == 0) {
                script.NextToPower();
                return;
            }
            if (type == 1) {
                script.NextToCarpenter();
                return;
            }
            if (type == 2) {
                script.NextToLab();
                return;
            }
            if (type == 3) {
                script.NextToFactory();
                return;
            }
            if (type == 4) {
                script.NextToGunsmith();
                return;
            }
            
        }
    }

    void OnTriggerExit2D(Collider2D hitInfo) {
        if (hitInfo.name == "Agent") {
            Debug.Log("adios");
            AgentController script = hitInfo.GetComponent<AgentController>();
            script.LeftBuilding();
        }
    }

    public void PowerOn() {
        anim.SetBool("PowerOn", true);
        sliderAnim1.SetBool("isOn", true);
        sliderAnim2.SetBool("isOn2", true);
    }

    public void Researching() {
        anim.SetBool("ResearchingOn", true);
    }

    public void ResearchDone() {
        anim.SetBool("ResearchingOn", false);
    }
}
