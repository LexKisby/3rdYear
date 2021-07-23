using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class crate : MonoBehaviour
{
    public bool isBig;
    public GameObject wood;
    public GameObject DeathAnim;
    public GameObject Coin;
    // Start is called before the first frame update
    public void OnTriggerEnter2D(Collider2D hitInfo)
    {
        if (hitInfo.name == "bullet1(Clone)")
        {
            bullet bullet = hitInfo.GetComponent<bullet>();
            if (bullet != null)
            {
                
                if (isBig) {
                    Instantiate(wood, transform.position + new Vector3(Random.value - 0.5f, Random.value - 0.5f, 0), Quaternion.identity);

                }
                Instantiate(wood, transform.position + new Vector3(Random.value - 0.5f, Random.value - 0.5f, 0), Quaternion.identity);
                Instantiate(wood, transform.position + new Vector3(Random.value - 0.5f, Random.value - 0.5f, 0), Quaternion.identity);
                GameObject DA = Instantiate(DeathAnim, transform.position, Quaternion.identity);
                Destroy(DA, 0.1f);
                if (Random.value > 0.7)
                {
                    Instantiate(Coin, transform.position, Quaternion.identity);
                }
                Destroy(gameObject);
            }
        }
    }
}
