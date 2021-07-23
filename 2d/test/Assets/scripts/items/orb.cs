using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class orb : MonoBehaviour
{
    // Start is called before the first frame update
    public GameObject prefab;
    
    void OnTriggerEnter2D(Collider2D hitInfo) {
        if (hitInfo.name == "Agent")
        {
            AgentController agent = hitInfo.GetComponent<AgentController>();
            if (agent != null) {
                agent.GotOrb();
                Destroy(gameObject);
                GameObject pickup = Instantiate(prefab, transform.position, Quaternion.identity);
                Destroy(pickup, 0.1f);
            }
        }
    }
}
