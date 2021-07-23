using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class wood : MonoBehaviour
{
    public GameObject pickup;

    // Start is called before the first frame update
    void OnTriggerEnter2D(Collider2D hitInfo) {
        if (hitInfo.name == "Agent") {
            AgentController script = hitInfo.GetComponent<AgentController>();
            script.PickUpWood();
            GameObject anim = Instantiate(pickup, transform.position, Quaternion.identity);
            Destroy(gameObject);
            Destroy(anim, 0.1f);
            
        }
    }
}
