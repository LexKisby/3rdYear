using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Coin : MonoBehaviour
{
    public GameObject ImpactPrefab;

    void OnTriggerEnter2D(Collider2D hitInfo)
    {
        AgentController agent = hitInfo.GetComponent<AgentController>();
        if (agent != null)
        {
            agent.PickUpCoin();
            Destroy(gameObject);

            GameObject impact = Instantiate(ImpactPrefab, transform.position, Quaternion.identity);
            impact.GetComponent<Rigidbody2D>().angularVelocity = 100f;
            Destroy(impact, 0.1f);
        }
    }
}
