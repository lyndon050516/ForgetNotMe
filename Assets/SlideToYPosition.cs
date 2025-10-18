using System.Collections;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(RectTransform))]
public class SlideToYPosition : MonoBehaviour
{
    [Header("Timing")]
    public float delay = 10f;        // wait before sliding
    public float duration = 8f;      // how long the slide takes (seconds)
    public AnimationCurve ease = AnimationCurve.EaseInOut(0, 0, 1, 1);

    [Header("Target Y Position")]
    public float targetY = 353f;     // exact Y position to end at

    private RectTransform rt;
    private Vector2 startPos;
    private Vector2 endPos;

    void Awake()
    {
        rt = GetComponent<RectTransform>();
    }

    IEnumerator Start()
    {
        // If this object is inside a layout group, prevent the layout from fighting
        LayoutElement le = GetComponent<LayoutElement>();
        bool addedLE = false;
        if (le == null)
        {
            le = gameObject.AddComponent<LayoutElement>();
            addedLE = true;
        }
        le.ignoreLayout = true;

        // Store the start and target positions
        startPos = rt.anchoredPosition;
        endPos = new Vector2(startPos.x, targetY);

        // Wait before moving
        yield return new WaitForSeconds(delay);

        float t = 0f;
        while (t < 1f)
        {
            t += Time.deltaTime / Mathf.Max(0.0001f, duration);
            float eased = ease.Evaluate(Mathf.Clamp01(t));
            rt.anchoredPosition = Vector2.LerpUnclamped(startPos, endPos, eased);
            yield return null;
        }

        // Snap exactly to final position
        rt.anchoredPosition = endPos;

        // Restore layout behavior
        le.ignoreLayout = false;
        if (addedLE) Destroy(le);
    }
}
