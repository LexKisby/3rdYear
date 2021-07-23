using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Cube : MonoBehaviour
{

    public int degreesPerSecond = 180;

    // Start is called before the first frame update
    //1 rotation per 2 seconds
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        transform.Rotate(Vector3.up * degreesPerSecond * Time.deltaTime, Space.Self);
        
        

    }
    public void SetSpeed(int speed) {
        degreesPerSecond = speed;
    }
}
