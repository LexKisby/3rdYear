using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class MenuLogic : MonoBehaviour
{
    bool showingControls = false;
    GameObject Controls;
    RectTransform rect;
    int Offset = 1300;

    void Start() {
        Controls = GameObject.FindGameObjectWithTag("controls");
        rect = Controls.GetComponent<RectTransform>();
        Cursor.lockState = CursorLockMode.Confined;
        Cursor.visible = true;
    }

    void Update() {
   if (showingControls) {
       if (Input.GetKeyDown(KeyCode.Space))
       {
           
           showingControls = false;
           rect.anchoredPosition = new Vector2(Offset, 0);
       }
   }
}

    public void ShowControls() {
        
        showingControls = true;
        rect.anchoredPosition = new Vector2(0, 0);

    }

    public void StartGame() {
        SceneManager.LoadScene("GameScene");
    }

}
