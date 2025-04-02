# ALGORITHM CrystalAngleDetection:

# FUNCTION ProcessImage(image):
#     1. Preprocessing
#     grayscale = ConvertToGrayscale(image)
#     enhanced = ApplyContrastEnhancement(grayscale)
#     denoised = ApplyGaussianBlur(enhanced)
    
#     2. Edge Detection
#     edges = ApplyCannyEdgeDetection(denoised)
    
#     3. Line Detection
#     rawLines = ApplyHoughTransform(edges)
    
#     4. Line Filtering
#     filteredLines = FilterLinesByAngle(rawLines)
    
#     5. Sub-pixel Refinement
#     refinedLines = RefineLinesToSubpixelAccuracy(filteredLines, edges)
    
#     6. Angle Calculation
#     angles = CalculateAngles(refinedLines)
    
#     7. Error Estimation
#     uncertainties = EstimateUncertaintyWithMonteCarlo(refinedLines)
    
#     8. Visualization (optional)
#     visualResult = CreateVisualization(image, edges, refinedLines, angles)
    
#     RETURN angles, uncertainties, visualResult
    
# FUNCTION RefineLinesToSubpixelAccuracy(lines, edgeImage):
#     refinedLines = []
    
#     FOR EACH line IN lines:
#         // Sample points along the line
#         samplePoints = SamplePointsAlongLine(line)
#         refinedPoints = []
        
#         FOR EACH point IN samplePoints:
#             // Extract small window around the point
#             window = ExtractWindow(edgeImage, point)
            
#             // Calculate center of mass of edge response
#             refinedPoint = CalculateCenterOfMass(window)
#             refinedPoints.ADD(refinedPoint)
        
#         // Fit a line through refined points
#         refinedLine = FitLine(refinedPoints)
#         refinedLines.ADD(refinedLine)
    
#     RETURN refinedLines

# FUNCTION CalculateAngles(lines):
#     angles = []
    
#     // Convert lines to vectors
#     vectors = LinesAsUnitVectors(lines)
    
#     // Calculate angles between adjacent vectors
#     FOR i = 0 TO length(vectors) - 1:
#         v1 = vectors[i]
#         v2 = vectors[(i+1) % length(vectors)]
        
#         dotProduct = v1 · v2  // Dot product
#         angle = ArcCosine(dotProduct)
#         angles.ADD(angle)
    
#     RETURN angles