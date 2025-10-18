using System.Collections;
using UnityEngine;
using UnityEngine.UI; // for LayoutElement

[RequireComponent(typeof(RectTransform))]
public class SlideDownSlightly : MonoBehaviour
{
    [Header("Timing")]
    public float delay = 10f;           // wait before sliding
    public float duration = 8f;         // how long the slide takes (seconds)

    [Header("Distance")]
    public bool useOwnHeight = true;    // slide by this element's height
    public float extraPixelsBelow = 48f; // and a little margin below

    [Header("Easing")]
    public AnimationCurve ease = AnimationCurve.EaseInOut(0, 0, 1, 1);

    RectTransform rt;
    Vector2 startPos;

    void Awake()
    {
        rt = GetComponent<RectTransform>();
    }

    IEnumerator Start()
    {
        // Don’t let layout fight us while we move
        LayoutElement le = GetComponent<LayoutElement>();
        bool addedLE = false;
        if (le == null)
        {
            le = gameObject.AddComponent<LayoutElement>();
            addedLE = true;
        }
        le.ignoreLayout = true;

        startPos = rt.anchoredPosition;

        // Wait (unscaled so timescale changes don’t matter)
        float w = 0f;
        while (w < delay) { w += Time.unscaledDeltaTime; yield return null; }

        // Compute a “just off screen” distance: element height + small margin
        float distance = (useOwnHeight ? rt.rect.height : 0f) + extraPixelsBelow;
        Vector2 endPos = startPos + Vector2.down * distance;

        // Animate
        float t = 0f;
        while (t < 1f)
        {
            t += Time.unscaledDeltaTime / Mathf.Max(0.0001f, duration);
            float k = ease.Evaluate(Mathf.Clamp01(t));
            rt.anchoredPosition = Vector2.LerpUnclamped(startPos, endPos, k);
            yield return null;
        }

        // Snap to exact end and restore layout participation
        rt.anchoredPosition = endPos;
        le.ignoreLayout = false;
        if (addedLE) Destroy(le);   // (optional) remove the helper component
    }
}
