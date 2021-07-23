using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class gate : MonoBehaviour
{
    public int g;
    // Start is called before the first frame update
    void OnCollisionEnter2D(Collision2D collInfo) {
        Collider2D hitInfo = collInfo.collider;
        if (hitInfo.name == "Agent") {
            Debug.Log("hello");
            hitInfo.GetComponent<AgentController>().AtGate(g);
        }
    }

    void OnCollisionExit2D(Collision2D collInfo) {
        Collider2D hitInfo = collInfo.collider;
        if (hitInfo.name == "Agent") {
            hitInfo.GetComponent<AgentController>().LeftGate();
        }
    }

    public void Open() {
        gameObject.GetComponent<Animator>().SetBool("isOpen", true);
        gameObject.GetComponent<BoxCollider2D>().enabled = false;

    }
}
