<?xml version="1.0" encoding="UTF-8"?>

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -->
<!--                                                                                   -->
<!--                  This file is part of the BMWi project 0328006                    -->
<!--                      Technical Capacities of Gas Networks                         -->
<!--                                                                                   -->
<!-- Copyright (C) 2013                                                                -->
<!-- FAU Erlangen-Nuremberg, HU Berlin, LU Hannover, TU Darmstadt,                     -->
<!-- University Duisburg-Essen, WIAS Berlin, Zuse Institute Berlin                     -->
<!-- Contact: Thorsten Koch (koch@zib.de)                                              -->
<!-- All rights reserved.                                                              -->
<!--                                                                                   -->
<!-- This work is licensed under the Creative Commons Attribution 3.0 Unported License.-->
<!-- To view a copy of this license, visit http://creativecommons.org/licenses/by/3.0/ -->
<!-- or send a letter to Creative Commons, 444 Castro Street, Suite 900, Mountain View,-->
<!-- California, 94041, USA.                                                           -->
<!--                                                                                   -->
<!--                         Please note that you have to cite                         -->
<!-- Pfetsch et al. (2012) "Validation of Nominations in Gas Network Optimization:     -->
<!-- Models, Methods, and Solutions", ZIB-Report 12-41                                 -->
<!--                               if you use this data                                -->
<!--                                                                                   -->
<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -->


<compressorStations xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xmlns="http://gaslib.zib.de/CompressorStations"
                    xsi:schemaLocation="http://gaslib.zib.de/CompressorStations
                                        http://gaslib.zib.de/schema/CompressorStations.xsd"
                    xmlns:gas="http://gaslib.zib.de/Gas"
                    xmlns:framework="http://gaslib.zib.de/CompressorStations">
  <compressorStation id="compressorStation_5">
    <compressors>
      <turboCompressor drive="drive_1" id="compressor_1">
        <speedMin value="4700" unit="per_min"/>
        <speedMax value="6500" unit="per_min"/>
        <n_isoline_coeff_1 value="0"/>
        <n_isoline_coeff_2 value="0.01357578307692308"/>
        <n_isoline_coeff_3 value="0"/>
        <n_isoline_coeff_4 value="0"/>
        <n_isoline_coeff_5 value="0"/>
        <n_isoline_coeff_6 value="0"/>
        <n_isoline_coeff_7 value="-5.394200581530082"/>
        <n_isoline_coeff_8 value="0.0002074692531357724"/>
        <n_isoline_coeff_9 value="0"/>
        <eta_ad_isoline_coeff_1 value="0.8555870230167826"/>
        <eta_ad_isoline_coeff_2 value="-1.860119222349977e-05"/>
        <eta_ad_isoline_coeff_3 value="4.801745725880117e-10"/>
        <eta_ad_isoline_coeff_4 value="0.0629620434625925"/>
        <eta_ad_isoline_coeff_5 value="1.997326294642135e-05"/>
        <eta_ad_isoline_coeff_6 value="-1.460270901018291e-09"/>
        <eta_ad_isoline_coeff_7 value="-0.107520438065594"/>
        <eta_ad_isoline_coeff_8 value="1.254578870690385e-05"/>
        <eta_ad_isoline_coeff_9 value="-5.141889351431648e-10"/>
        <surgeline_coeff_1 value="39.67013512365385"/>
        <surgeline_coeff_2 value="118.4558063871487"/>
        <surgeline_coeff_3 value="0"/>
        <chokeline_coeff_1 value="-43.00857215851677"/>
        <chokeline_coeff_2 value="16.08792455583167"/>
        <chokeline_coeff_3 value="0"/>
        <efficiencyOfChokeline value="0.5"/>
        <surgelineMeasurements>
          <measurement>
            <speed value="4700" unit="per_min"/>
            <adiabaticHead value="63.62545284932694" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2022300000000003" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="4925" unit="per_min"/>
            <adiabaticHead value="66.63417411780011" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.227629525445294" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5150" unit="per_min"/>
            <adiabaticHead value="69.63841612325412" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2529912371003163" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5375" unit="per_min"/>
            <adiabaticHead value="72.63837750604272" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2783168118803641" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5600" unit="per_min"/>
            <adiabaticHead value="75.63425458459778" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3036079070991468" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5825" unit="per_min"/>
            <adiabaticHead value="78.62624145715135" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3288661613275202" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="6050" unit="per_min"/>
            <adiabaticHead value="81.61453010058334" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3540931952279553" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="6275" unit="per_min"/>
            <adiabaticHead value="84.59931046654521" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.379290612366012" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="6500" unit="per_min"/>
            <adiabaticHead value="87.580770575" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.4044600000000002" unit="m_cube_per_s"/>
          </measurement>
        </surgelineMeasurements>
        <characteristicDiagramMeasurements>
          <adiabaticEfficiency value="0.82">
            <measurement>
              <speed value="4700" unit="per_min"/>
              <adiabaticHead value="61.96803682060428" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6449455485471374" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4925" unit="per_min"/>
              <adiabaticHead value="64.83728783649175" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6802756277330363" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5150" unit="per_min"/>
              <adiabaticHead value="67.70056641982177" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7155321662931695" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5375" unit="per_min"/>
              <adiabaticHead value="70.55824457481457" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7507197448440412" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5600" unit="per_min"/>
              <adiabaticHead value="73.41068764679514" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7858428620088779" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5825" unit="per_min"/>
              <adiabaticHead value="76.25825471288232" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8209059392283174" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6050" unit="per_min"/>
              <adiabaticHead value="79.1012989559225" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8559133253647847" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6275" unit="per_min"/>
              <adiabaticHead value="81.94016802284904" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8908693011150943" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6500" unit="per_min"/>
              <adiabaticHead value="84.77520436856508" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9257780832447989" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.82">
            <measurement>
              <speed value="4700" unit="per_min"/>
              <adiabaticHead value="58.44298126099858" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.101654189681931" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4925" unit="per_min"/>
              <adiabaticHead value="61.11589369796927" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.146247042491944" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5150" unit="per_min"/>
              <adiabaticHead value="63.78211164128105" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.190728209424695" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5375" unit="per_min"/>
              <adiabaticHead value="66.44218531331167" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.235106869974866" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5600" unit="per_min"/>
              <adiabaticHead value="69.096651885863" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.279391985911187" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5825" unit="per_min"/>
              <adiabaticHead value="71.74603642906993" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.323592317107314" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6050" unit="per_min"/>
              <adiabaticHead value="74.39085280650491" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.367716436475076" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6275" unit="per_min"/>
              <adiabaticHead value="77.03160452121269" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.411772744079082" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6500" unit="per_min"/>
              <adiabaticHead value="79.6687855169889" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.455769480504647" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.82">
            <measurement>
              <speed value="4700" unit="per_min"/>
              <adiabaticHead value="53.11701103290997" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.555268252770686" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4925" unit="per_min"/>
              <adiabaticHead value="55.55443777734875" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.608049714847537" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5150" unit="per_min"/>
              <adiabaticHead value="57.9853709262641" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.660690560814941" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5375" unit="per_min"/>
              <adiabaticHead value="60.41049732704857" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.713205664067427" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5600" unit="per_min"/>
              <adiabaticHead value="62.83048444213067" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.765609478226191" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5825" unit="per_min"/>
              <adiabaticHead value="65.24598200579811" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.817916073016917" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6050" unit="per_min"/>
              <adiabaticHead value="67.65762356831736" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.870139167707041" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6275" unit="per_min"/>
              <adiabaticHead value="70.06602793895597" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.922292162353799" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6500" unit="per_min"/>
              <adiabaticHead value="72.47180053829869" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.974388167088075" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.82">
            <measurement>
              <speed value="4700" unit="per_min"/>
              <adiabaticHead value="46.28753711440974" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.991056398915666" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4925" unit="per_min"/>
              <adiabaticHead value="48.47124183192329" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.050804099852424" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5150" unit="per_min"/>
              <adiabaticHead value="50.64938633229039" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.110399669327201" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5375" unit="per_min"/>
              <adiabaticHead value="52.82272832201451" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.169863838724238" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5600" unit="per_min"/>
              <adiabaticHead value="54.99200203781332" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.229216697277887" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5825" unit="per_min"/>
              <adiabaticHead value="57.1579205189996" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.288477754246553" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6050" unit="per_min"/>
              <adiabaticHead value="59.32117770687695" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.347665996353644" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6275" unit="per_min"/>
              <adiabaticHead value="61.48245039104698" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.406799941039905" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6500" unit="per_min"/>
              <adiabaticHead value="63.64240002019311" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.465897686007745" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.74">
            <measurement>
              <speed value="4700" unit="per_min"/>
              <adiabaticHead value="38.37358245917406" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.398991393156468" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4925" unit="per_min"/>
              <adiabaticHead value="40.30282412247502" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.464542227764651" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5150" unit="per_min"/>
              <adiabaticHead value="42.22781609315246" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.529948668384461" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5375" unit="per_min"/>
              <adiabaticHead value="44.14932413755389" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.595236733852288" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5600" unit="per_min"/>
              <adiabaticHead value="46.0680894948332" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.66043160963147" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5825" unit="per_min"/>
              <adiabaticHead value="47.98483150251623" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.725557737022482" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6050" unit="per_min"/>
              <adiabaticHead value="49.90025000916567" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.790638895139294" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6275" unit="per_min"/>
              <adiabaticHead value="51.81502760059976" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.855698276550741" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6500" unit="per_min"/>
              <adiabaticHead value="53.72983166279987" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.920758557372997" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.6599999999999999">
            <measurement>
              <speed value="4700" unit="per_min"/>
              <adiabaticHead value="29.8018251385575" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.773962586754131" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4925" unit="per_min"/>
              <adiabaticHead value="31.48728805507782" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.8443170639022" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5150" unit="per_min"/>
              <adiabaticHead value="33.16986692493138" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.914551155372647" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5375" unit="per_min"/>
              <adiabaticHead value="34.85029020287771" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.984695268273948" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5600" unit="per_min"/>
              <adiabaticHead value="36.52926323207118" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.054778844991545" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5825" unit="per_min"/>
              <adiabaticHead value="38.20747094028572" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.124830475733471" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6050" unit="per_min"/>
              <adiabaticHead value="39.88558031117561" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.194878001685555" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6275" unit="per_min"/>
              <adiabaticHead value="41.56424266011499" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.264948610009351" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6500" unit="per_min"/>
              <adiabaticHead value="43.24409574030209" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.335068921755" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.58">
            <measurement>
              <speed value="4700" unit="per_min"/>
              <adiabaticHead value="20.93542167391494" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.11468342453207" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4925" unit="per_min"/>
              <adiabaticHead value="22.39370949832732" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.189028202507537" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5150" unit="per_min"/>
              <adiabaticHead value="23.85033112253325" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.263288036151483" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5375" unit="per_min"/>
              <adiabaticHead value="25.305951156128" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.33749680783745" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5600" unit="per_min"/>
              <adiabaticHead value="26.76121395353948" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.411687367312985" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5825" unit="per_min"/>
              <adiabaticHead value="28.21674617071592" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.485891662041788" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6050" unit="per_min"/>
              <adiabaticHead value="29.67315910754405" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.560140856622231" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6275" unit="per_min"/>
              <adiabaticHead value="31.13105086532617" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.634465442777403" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6500" unit="per_min"/>
              <adiabaticHead value="32.59100834474299" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.70889534121299" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.5">
            <measurement>
              <speed value="4700" unit="per_min"/>
              <adiabaticHead value="12.04913204890597" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.4223" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4925" unit="per_min"/>
              <adiabaticHead value="13.2989881165551" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.499989080608977" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5150" unit="per_min"/>
              <adiabaticHead value="14.54815730356353" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.57763546580138" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5375" unit="per_min"/>
              <adiabaticHead value="15.79722810845567" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.655275735716704" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5600" unit="per_min"/>
              <adiabaticHead value="17.04677217493282" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.732945422825238" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5825" unit="per_min"/>
              <adiabaticHead value="18.29734658828095" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.810679154669152" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6050" unit="per_min"/>
              <adiabaticHead value="19.54949598169556" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.888510784788322" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6275" unit="per_min"/>
              <adiabaticHead value="20.80375447942028" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.966473513502765" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6500" unit="per_min"/>
              <adiabaticHead value="22.06064750000001" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.0446" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
        </characteristicDiagramMeasurements>
      </turboCompressor>
      <pistonCompressor drive="drive_2" id="compressor_2">
        <speedMin unit="per_min" value="165"/>
        <speedMax unit="per_min" value="350"/>
        <operatingVolume unit="m_cube" value="0.5"/>
        <maximalTorque unit="kNm" value="0"/>
        <maximalCompressionRatio value="2"/>
        <adiabaticEfficiency value="0.95"/>
        <additionalReductionVolFlow value="0.35"/>
      </pistonCompressor>
    </compressors>
    <drives>
      <gasTurbine id="drive_1">
        <energy_rate_fun_coeff_1 value="4635.09742"/>
        <energy_rate_fun_coeff_2 value="2.88577"/>
        <energy_rate_fun_coeff_3 value="-2.85112e-18"/>
        <power_fun_coeff_1 value="-1496.222462872491"/>
        <power_fun_coeff_2 value="4.848886009147775"/>
        <power_fun_coeff_3 value="-0.0002941451299068079"/>
        <power_fun_coeff_4 value="9.000675834411878"/>
        <power_fun_coeff_5 value="-0.02916895863370923"/>
        <power_fun_coeff_6 value="1.769459440863755e-06"/>
        <power_fun_coeff_7 value="-0.02991526481799991"/>
        <power_fun_coeff_8 value="9.694795569200874e-05"/>
        <power_fun_coeff_9 value="-5.881097012267645e-09"/>
      </gasTurbine>
      <gasDrivenMotor id="drive_2">
        <energy_rate_fun_coeff_1 value="2629"/>
        <energy_rate_fun_coeff_2 value="2.47428571429"/>
        <energy_rate_fun_coeff_3 value="1.37142857143e-05"/>
        <power_fun_coeff_1 value="230.514705882"/>
        <power_fun_coeff_2 value="24.4195632799"/>
        <power_fun_coeff_3 value="0.00423351158645"/>
        <specificEnergyConsumptionMeasurements>
          <measurement>
            <compressorPower unit="kW" value="5250"/>
            <fuelConsumption unit="kW" value="15997"/>
          </measurement>
          <measurement>
            <compressorPower unit="kW" value="7000"/>
            <fuelConsumption unit="kW" value="20621"/>
          </measurement>
          <measurement>
            <compressorPower unit="kW" value="8750"/>
            <fuelConsumption unit="kW" value="25329"/>
          </measurement>
        </specificEnergyConsumptionMeasurements>
        <maximalPowerMeasurements>
          <measurement>
            <speed unit="per_min" value="165"/>
            <maximalPower unit="kW" value="4375"/>
          </measurement>
          <measurement>
            <speed unit="per_min" value="250"/>
            <maximalPower unit="kW" value="6600"/>
          </measurement>
          <measurement>
            <speed unit="per_min" value="330"/>
            <maximalPower unit="kW" value="8750"/>
          </measurement>
        </maximalPowerMeasurements>
      </gasDrivenMotor>
    </drives>
    <configurations>
      <configuration nrOfSerialStages="1" confId="config_1">
        <stage nrOfParallelUnits="1" stageNr="1">
          <compressor nominalSpeed="350" id="compressor_2"/>
        </stage>
      </configuration>
      <configuration nrOfSerialStages="1" confId="config_2">
        <stage nrOfParallelUnits="1" stageNr="1">
          <compressor nominalSpeed="6500" id="compressor_1"/>
        </stage>
      </configuration>
      <configuration nrOfSerialStages="1" confId="config_3">
        <stage nrOfParallelUnits="2" stageNr="1">
          <compressor nominalSpeed="350" id="compressor_2"/>
          <compressor nominalSpeed="6500" id="compressor_1"/>
        </stage>
      </configuration>
    </configurations>
  </compressorStation>
  <compressorStation id="compressorStation_2">
    <compressors>
      <turboCompressor drive="drive_3" id="compressor_3">
        <speedMin value="3445" unit="per_min"/>
        <speedMax value="12000" unit="per_min"/>
        <n_isoline_coeff_1 value="0"/>
        <n_isoline_coeff_2 value="0.003177244166666667"/>
        <n_isoline_coeff_3 value="0"/>
        <n_isoline_coeff_4 value="0"/>
        <n_isoline_coeff_5 value="0"/>
        <n_isoline_coeff_6 value="0"/>
        <n_isoline_coeff_7 value="-0.5123807332038738"/>
        <n_isoline_coeff_8 value="1.067459860841404e-05"/>
        <n_isoline_coeff_9 value="0"/>
        <eta_ad_isoline_coeff_1 value="0.8637491069216806"/>
        <eta_ad_isoline_coeff_2 value="-4.070585986640928e-05"/>
        <eta_ad_isoline_coeff_3 value="2.129311035503427e-09"/>
        <eta_ad_isoline_coeff_4 value="0.01623108561186756"/>
        <eta_ad_isoline_coeff_5 value="3.078331395067538e-05"/>
        <eta_ad_isoline_coeff_6 value="-2.055999497897171e-09"/>
        <eta_ad_isoline_coeff_7 value="-0.05867563337968518"/>
        <eta_ad_isoline_coeff_8 value="4.27362301858818e-06"/>
        <eta_ad_isoline_coeff_9 value="-5.522129231291596e-11"/>
        <surgeline_coeff_1 value="-16.12671835897396"/>
        <surgeline_coeff_2 value="62.56253783122806"/>
        <surgeline_coeff_3 value="0"/>
        <chokeline_coeff_1 value="-5.335784422395831"/>
        <chokeline_coeff_2 value="1.723530282441379"/>
        <chokeline_coeff_3 value="0"/>
        <efficiencyOfChokeline value="0.3"/>
        <surgelineMeasurements>
          <measurement>
            <speed value="3445" unit="per_min"/>
            <adiabaticHead value="10.85712983301307" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.4313100000000007" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="4514.375" unit="per_min"/>
            <adiabaticHead value="14.2339537255835" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.485285174435538" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5583.75" unit="per_min"/>
            <adiabaticHead value="17.60928062981854" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.5392364210000635" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="6653.125" unit="per_min"/>
            <adiabaticHead value="20.98331093930939" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.5931669427860052" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="7722.500000000001" unit="per_min"/>
            <adiabaticHead value="24.35624427892195" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.6470799305984811" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="8791.875" unit="per_min"/>
            <adiabaticHead value="27.72827958545994" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.7009785642446189" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="9861.25" unit="per_min"/>
            <adiabaticHead value="31.09961518749274" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.7548660138095243" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="10930.625" unit="per_min"/>
            <adiabaticHead value="34.47044888443925" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.8087454409203594" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="12000" unit="per_min"/>
            <adiabaticHead value="37.84097802499985" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.8626199999999976" unit="m_cube_per_s"/>
          </measurement>
        </surgelineMeasurements>
        <characteristicDiagramMeasurements>
          <adiabaticEfficiency value="0.7825">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="10.61330386568697" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8358775581800651" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="13.90259633233582" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9743404230632964" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="17.18072346371341" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.112333282823932" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="20.44906999138614" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.249914427778725" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="23.70898333931381" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.387140577779615" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="26.96177795500484" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.524067064533829" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="30.20873936268458" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.660748002222128" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="33.45112797523899" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.797236447962693" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="36.69018269790396" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.933584553508526" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.785">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="10.15255152724189" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.291301188994941" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="13.27069629420914" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.520075884331265" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="16.35953340417996" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.746700310580851" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="19.42315777884365" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.971474907438426" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="22.46538189191527" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.19467939171569" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="25.48977972164964" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.416575982086725" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="28.49972443869463" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.63741216420244" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="31.49842106214161" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.857423086627437" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="34.48893506455301" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.076833659557986" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.7875000000000001">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="9.423414552232879" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.789001316095746" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="12.2812245547681" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.107660485658844" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="15.08793444367331" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.420621753766118" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="17.85200376225234" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.728828399026602" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="20.58086923819632" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.033109651328994" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="23.28115814679517" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.334204482836762" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="25.9588540717571" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.632780091094101" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="28.61942809147523" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.929446526907687" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="31.26794451544314" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.224768484451098" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.79">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="8.400377938632207" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.3133394486285" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="10.92284431729544" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.714510639718638" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="13.37646137889" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.10473208623822" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="15.77466226065789" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.486140184419533" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="18.12856982304092" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.860503905777723" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="20.44760329708358" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.229321277865997" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="22.73990662398119" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.593887507081208" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="25.01265999927604" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.955344526422869" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="27.27231279987609" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.314718040034293" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.6675">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="7.09716555087797" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.844581579041392" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="9.239700208210518" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.315801042311378" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="11.30531719330826" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.77010357772565" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="13.31117595270565" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.211263156994913" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="15.27074877435345" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.642242814707869" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="17.1949587528852" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.065444927308166" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="19.09292005721057" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.48287402422876" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="20.97244019790363" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.896247254328649" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="22.84037378046652" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.307072188799079" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.545">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="5.564472474744838" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.363666189065935" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="7.316721385497756" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.890652504256555" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="8.99433291430438" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.395191735219597" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="10.61570708233759" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.882817661601218" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="12.19469888712596" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.357697153787099" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="13.7421794569335" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.823099687814955" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="15.26698923738497" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.281684014867817" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="16.77655203674789" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.735682834500857" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="18.27728923442433" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.187027367243742" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.4225">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="3.873716862612785" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.856059494367554" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="5.252004914733872" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.425512428435082" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="6.56535000737702" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.968133555635512" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="7.830948371983267" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.491027663994783" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="9.061367875555698" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.99938728835992" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="10.26625077019855" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.497196217709813" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="11.45330737689634" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.987640045143436" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="12.62893362864934" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.473361311751893" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="13.79861569816198" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.956626682430471" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.3">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="2.097974038802082" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.3131" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="3.133810663029482" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.914097055160608" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="4.118108079996595" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.485190831112637" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="5.065222827214804" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.034711055310044" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="5.985442780063921" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.568626799189882" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="6.886549996272761" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.091453247549365" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="7.774705565454958" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.606765092215143" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="8.654986753623117" unit="kJ_per_kg"/>
              <volumetricFlowrate value="8.117508185699547" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="9.531732499999993" unit="kJ_per_kg"/>
              <volumetricFlowrate value="8.626199999999999" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
        </characteristicDiagramMeasurements>
      </turboCompressor>
      <turboCompressor drive="drive_4" id="compressor_4">
        <speedMin value="3445" unit="per_min"/>
        <speedMax value="12000" unit="per_min"/>
        <n_isoline_coeff_1 value="0"/>
        <n_isoline_coeff_2 value="0.006353910833333334"/>
        <n_isoline_coeff_3 value="0"/>
        <n_isoline_coeff_4 value="0"/>
        <n_isoline_coeff_5 value="0"/>
        <n_isoline_coeff_6 value="0"/>
        <n_isoline_coeff_7 value="-4.349478469203576"/>
        <n_isoline_coeff_8 value="9.061413477507449e-05"/>
        <n_isoline_coeff_9 value="0"/>
        <eta_ad_isoline_coeff_1 value="0.847304306013587"/>
        <eta_ad_isoline_coeff_2 value="-3.398590798968556e-05"/>
        <eta_ad_isoline_coeff_3 value="1.783301969657632e-09"/>
        <eta_ad_isoline_coeff_4 value="0.04909045177930035"/>
        <eta_ad_isoline_coeff_5 value="5.048034415004849e-05"/>
        <eta_ad_isoline_coeff_6 value="-3.442806444517018e-09"/>
        <eta_ad_isoline_coeff_7 value="-0.2108561683890049"/>
        <eta_ad_isoline_coeff_8 value="1.569027826151143e-05"/>
        <eta_ad_isoline_coeff_9 value="-2.204237820474443e-10"/>
        <surgeline_coeff_1 value="-32.25050550480731"/>
        <surgeline_coeff_2 value="257.7696709494072"/>
        <surgeline_coeff_3 value="0"/>
        <chokeline_coeff_1 value="-10.67059900572916"/>
        <chokeline_coeff_2 value="7.101275766254068"/>
        <chokeline_coeff_3 value="0"/>
        <efficiencyOfChokeline value="0.4"/>
        <surgelineMeasurements>
          <measurement>
            <speed value="3445" unit="per_min"/>
            <adiabaticHead value="21.71228626009514" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2093449999999953" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="4514.375" unit="per_min"/>
            <adiabaticHead value="28.46532026936809" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2355429385875741" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5583.75" unit="per_min"/>
            <adiabaticHead value="35.21536057406497" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2617292633007779" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="6653.125" unit="per_min"/>
            <adiabaticHead value="41.96280792494235" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2879055288250556" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="7722.500000000001" unit="per_min"/>
            <adiabaticHead value="48.70806153545225" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.314073283881987" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="8791.875" unit="per_min"/>
            <adiabaticHead value="55.45151924303859" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3402340718550216" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="9861.25" unit="per_min"/>
            <adiabaticHead value="62.19357766879337" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3663894314088539" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="10930.625" unit="per_min"/>
            <adiabaticHead value="68.93463237560594" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3925408971029528" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="12000" unit="per_min"/>
            <adiabaticHead value="75.67507802499991" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.4186899999999996" unit="m_cube_per_s"/>
          </measurement>
        </surgelineMeasurements>
        <characteristicDiagramMeasurements>
          <adiabaticEfficiency value="0.785">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="21.22467864356675" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4057100169650734" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="27.80266571082095" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4729157586566188" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="34.35832413695817" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.5398933738906495" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="40.89442313342102" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6066711550470375" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="47.41365730321951" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6732766322489043" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="53.91865530245433" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7397366618553597" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="60.41198794591801" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.806077509274517" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="66.89617583028827" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8723249268478597" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="73.37369654085187" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9385042274796391" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.79">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="20.30325771361618" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6267590536044741" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="26.53898048953389" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7377994621161779" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="32.71609327845625" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8477961941957023" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="38.84278517946365" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.956895074303163" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="44.92668044702607" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.065231868629805" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="50.97492638804231" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.172933850293167" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="56.99426873069612" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.280121141441098" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="62.99111693062191" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.386907876168001" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="68.97160137576033" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.493403219169892" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.795">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="18.84511629247572" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8683278396468054" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="24.56021685831206" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.022995489022398" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="30.17312648491105" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.174897547105721" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="35.70076272126269" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.324491853178048" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="41.15799767104011" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.472180890676006" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="46.558084680241" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.618323334630455" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="51.91298982869798" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.763243022814437" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="57.23365427876687" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.907236055680344" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="62.53020572893953" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.050576518924705" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.8">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="16.79922901372952" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.122825918418616" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="21.84370328431174" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.317542440175044" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="26.75049143489733" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.506944282751478" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="31.54645729834593" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.692068389110633" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="36.25384457383571" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.873773365224635" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="40.89149001140405" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.052786308953785" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="45.47568001318835" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.229735874823016" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="50.02077366519151" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.405176323025191" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="54.53966854898245" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.579605499735639" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.7000000000000001">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="14.19304111178645" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.380674991686768" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="18.47772099658727" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.609390853916383" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="22.60857951757384" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.829895744311461" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="26.61993244889194" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.044021436092601" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="30.53872191770261" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.253206097806725" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="34.38679212787722" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.458615771272004" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="38.18236976063193" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.661223395242794" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="41.94106841801172" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.861862422520763" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="45.67659606511896" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.061264583163253" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.6000000000000001">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="11.12793354379167" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.632623167443389" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="14.63211287427419" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.88840659503278" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="17.98703100705098" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.13329487795216" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="21.22948464005623" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.369973947666196" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="24.38718125004483" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.600466278684844" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="27.48186111759451" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.826358777087528" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="30.53120352710395" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.048941921338487" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="33.55005474574729" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.269299397158846" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="36.5512563651704" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.488368561349472" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.5">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="7.746729633449551" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.871616180585601" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="10.50305521827668" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.14801163740869" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="13.12950668826404" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.411383736070381" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="15.66047338068452" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.665180928610484" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="18.12108874519254" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.911923516453844" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="20.53063553340841" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.153545111860288" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="22.90453298586324" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.391591906634561" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="25.25557180602458" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.627346511346132" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="27.59472334212741" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.861909097478396" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.4">
            <measurement>
              <speed value="3445" unit="per_min"/>
              <adiabaticHead value="4.195566747135425" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.09345" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4514.375" unit="per_min"/>
              <adiabaticHead value="6.267051720588643" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.385156031653793" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5583.75" unit="per_min"/>
              <adiabaticHead value="8.23546764735412" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.662347904150784" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6653.125" unit="per_min"/>
              <adiabaticHead value="10.12952499299182" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.929068618566416" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7722.500000000001" unit="per_min"/>
              <adiabaticHead value="11.96979763832387" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.188215384007803" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8791.875" unit="per_min"/>
              <adiabaticHead value="13.77184828433105" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.441979736403565" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9861.25" unit="per_min"/>
              <adiabaticHead value="15.54799799039301" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.692096724466808" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10930.625" unit="per_min"/>
              <adiabaticHead value="17.30840036568456" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.939996177077442" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="19.0617325" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.1869" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
        </characteristicDiagramMeasurements>
      </turboCompressor>
    </compressors>
    <drives>
      <gasTurbine id="drive_3">
        <energy_rate_fun_coeff_1 value="4635.09742"/>
        <energy_rate_fun_coeff_2 value="2.88577"/>
        <energy_rate_fun_coeff_3 value="-2.85112e-18"/>
        <power_fun_coeff_1 value="-1716.279797872292"/>
        <power_fun_coeff_2 value="3.012770186822614"/>
        <power_fun_coeff_3 value="-9.899603565330603e-05"/>
        <power_fun_coeff_4 value="10.32445273688883"/>
        <power_fun_coeff_5 value="-0.01812362030918244"/>
        <power_fun_coeff_6 value="5.9552055119976e-07"/>
        <power_fun_coeff_7 value="-0.03431506071400858"/>
        <power_fun_coeff_8 value="6.02369100925965e-05"/>
        <power_fun_coeff_9 value="-1.979313033982428e-09"/>
      </gasTurbine>
      <gasTurbine id="drive_4">
        <energy_rate_fun_coeff_1 value="1925.34811"/>
        <energy_rate_fun_coeff_2 value="2.66198"/>
        <energy_rate_fun_coeff_3 value="2.22172e-19"/>
        <power_fun_coeff_1 value="-1431.594203043916"/>
        <power_fun_coeff_2 value="2.513030998736795"/>
        <power_fun_coeff_3 value="-8.257520186469461e-05"/>
        <power_fun_coeff_4 value="8.611898075159164"/>
        <power_fun_coeff_5 value="-0.01511738925375686"/>
        <power_fun_coeff_6 value="4.967393836063389e-07"/>
        <power_fun_coeff_7 value="-0.0286230963367257"/>
        <power_fun_coeff_8 value="5.02451939390919e-05"/>
        <power_fun_coeff_9 value="-1.650997156157959e-09"/>
      </gasTurbine>
    </drives>
    <configurations>
      <configuration nrOfSerialStages="1" confId="config_1">
        <stage nrOfParallelUnits="1" stageNr="1">
          <compressor nominalSpeed="10000" id="compressor_3"/>
        </stage>
      </configuration>
      <configuration nrOfSerialStages="1" confId="config_2">
        <stage nrOfParallelUnits="1" stageNr="1">
          <compressor nominalSpeed="10000" id="compressor_4"/>
        </stage>
      </configuration>
    </configurations>
  </compressorStation>
  <compressorStation id="compressorStation_1">
    <compressors>
      <turboCompressor drive="drive_5" id="compressor_5">
        <speedMin value="3435" unit="per_min"/>
        <speedMax value="12000" unit="per_min"/>
        <n_isoline_coeff_1 value="0"/>
        <n_isoline_coeff_2 value="0.003188014166666666"/>
        <n_isoline_coeff_3 value="0"/>
        <n_isoline_coeff_4 value="0"/>
        <n_isoline_coeff_5 value="0"/>
        <n_isoline_coeff_6 value="0"/>
        <n_isoline_coeff_7 value="-0.5141533271582497"/>
        <n_isoline_coeff_8 value="1.07115276491302e-05"/>
        <n_isoline_coeff_9 value="0"/>
        <eta_ad_isoline_coeff_1 value="0.8630817294694793"/>
        <eta_ad_isoline_coeff_2 value="-4.05765770813442e-05"/>
        <eta_ad_isoline_coeff_3 value="2.123473967944464e-09"/>
        <eta_ad_isoline_coeff_4 value="0.01679986550905961"/>
        <eta_ad_isoline_coeff_5 value="3.065956036154658e-05"/>
        <eta_ad_isoline_coeff_6 value="-2.04979823989363e-09"/>
        <eta_ad_isoline_coeff_7 value="-0.05864373275262806"/>
        <eta_ad_isoline_coeff_8 value="4.272140881485123e-06"/>
        <eta_ad_isoline_coeff_9 value="-5.531351804537067e-11"/>
        <surgeline_coeff_1 value="-16.24518371417187"/>
        <surgeline_coeff_2 value="62.85075463333899"/>
        <surgeline_coeff_3 value="0"/>
        <chokeline_coeff_1 value="-5.421616592187505"/>
        <chokeline_coeff_2 value="1.737286438770159"/>
        <chokeline_coeff_3 value="0"/>
        <efficiencyOfChokeline value="0.3"/>
        <surgelineMeasurements>
          <measurement>
            <speed value="3435" unit="per_min"/>
            <adiabaticHead value="10.86203250541377" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.4312949999999953" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="4505.625" unit="per_min"/>
            <adiabaticHead value="14.25428585667687" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.4852681522883482" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5576.25" unit="per_min"/>
            <adiabaticHead value="17.64503799454942" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.5392174192089069" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="6646.875" unit="per_min"/>
            <adiabaticHead value="21.03449021972509" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.5931460035982141" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="7717.5" unit="per_min"/>
            <adiabaticHead value="24.42284306191394" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.6470570960259177" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="8788.125" unit="per_min"/>
            <adiabaticHead value="27.81029636086331" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.7009538760838696" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="9858.75" unit="per_min"/>
            <adiabaticHead value="31.19704934653861" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.7548395136618599" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="10929.375" unit="per_min"/>
            <adiabaticHead value="34.58330071856417" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.8087171702115766" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="12000" unit="per_min"/>
            <adiabaticHead value="37.969248725" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.8625900000000001" unit="m_cube_per_s"/>
          </measurement>
        </surgelineMeasurements>
        <characteristicDiagramMeasurements>
          <adiabaticEfficiency value="0.7825">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="10.61717668115234" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8360344857184826" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="13.92161058771909" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.974447188217101" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="17.214854351131" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.112391169597609" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="20.49829770352658" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.249924641519394" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="23.7732930133354" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.387104250589533" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="27.04115962624748" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.523985260192813" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="30.30318792805691" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.660621720671917" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="33.56064316616958" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.797066629398781" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="36.81476906278338" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.933372082119736" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.785">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="10.15454536969627" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.29154975043712" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="13.28730479091513" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.520209339143426" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="16.39069639093454" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.746725375468663" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="19.46882700761108" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.9713976168244" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="22.52552081523288" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.194505189055393" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="25.5643633059517" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.416309796636992" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="28.58873901217877" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.637058476026539" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="31.60186420103353" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.856985982025732" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="34.60681552052048" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.07631687866031" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.7875000000000001">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="9.422598243510489" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.789253016088827" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="12.29426328403119" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.107729689327374" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="15.11472039115851" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.420527241902327" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="17.89244982159159" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.728586160919123" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="20.6349086064022" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.032733454547054" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="23.34874385926057" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.333706308571529" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="26.03995856170941" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.632170472501722" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="28.71404281970721" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.92873481633351" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="31.37607969698518" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.223963067801201" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.79">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="8.39581963772342" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.313521592682003" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="10.93117467520518" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.714459502302576" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="13.39751585665769" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.104483646094631" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="15.80830823615558" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.48572337105447" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="18.17470547427045" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.859942503268806" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="20.50615623652576" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.228635243016369" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="22.81083258783135" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.593093910533886" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="25.09594172919348" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.954458243673829" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="27.36795917629311" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.313752272476353" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.6675">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="7.088003502139169" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.84465671016362" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="9.242294020381276" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.315621233622216" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="11.31944573174409" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.76972190277962" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="13.33666424864884" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.210720156952473" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="15.30746443318948" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.64157057470471" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="17.24280840660733" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.064669662061307" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="19.15184630993983" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.482017795376695" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="21.04241918056329" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.895329158694341" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="22.92141331120877" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.306109212650599" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.545">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="5.549966601138379" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.363635138602215" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="7.312728152997536" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.89037407313008" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="9.000587995131815" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.39473128125077" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="10.63200715953203" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.882223189341335" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="12.22089359431129" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.357005695721003" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="13.77816470515186" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.822341080889835" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="15.31270202035636" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.280883275409317" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="16.83196653268129" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.73486173304246" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="18.34241399035793" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.186205525785045" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.4225">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="3.85328532596975" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.85594973969543" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="5.24079847653941" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.425183586358053" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="6.563083030830983" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.96765709222208" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="7.837407526434269" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.490454756684467" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="9.076399092666803" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.998756919398769" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="10.28974963419" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.496539730190765" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="11.48521217137707" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.986983902416932" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="12.66922037115475" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.472728878428748" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="13.84729467300666" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.95603944469057" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.3">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="2.071212953906251" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.31295" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="3.115004089640486" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.913766947879443" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="4.10697080419604" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.484753224188476" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="5.061547266426997" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.034217285455605" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="5.989082090393532" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.568115900713976" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="6.89740655408664" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.090956834380688" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="7.792723046794668" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.606310245728233" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="8.68014467486061" unit="kJ_per_kg"/>
              <volumetricFlowrate value="8.117119291526205" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="9.564042500000005" unit="kJ_per_kg"/>
              <volumetricFlowrate value="8.625899999999998" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
        </characteristicDiagramMeasurements>
      </turboCompressor>
      <turboCompressor drive="drive_6" id="compressor_6">
        <speedMin value="3435" unit="per_min"/>
        <speedMax value="12000" unit="per_min"/>
        <n_isoline_coeff_1 value="0"/>
        <n_isoline_coeff_2 value="0.006362339999999999"/>
        <n_isoline_coeff_3 value="0"/>
        <n_isoline_coeff_4 value="0"/>
        <n_isoline_coeff_5 value="0"/>
        <n_isoline_coeff_6 value="0"/>
        <n_isoline_coeff_7 value="-4.351506197530798"/>
        <n_isoline_coeff_8 value="9.065637911522494e-05"/>
        <n_isoline_coeff_9 value="0"/>
        <eta_ad_isoline_coeff_1 value="0.8467461236811562"/>
        <eta_ad_isoline_coeff_2 value="-3.387764145964746e-05"/>
        <eta_ad_isoline_coeff_3 value="1.778397709413836e-09"/>
        <eta_ad_isoline_coeff_4 value="0.05000707485583122"/>
        <eta_ad_isoline_coeff_5 value="5.025072831711835e-05"/>
        <eta_ad_isoline_coeff_6 value="-3.4308086631544e-09"/>
        <eta_ad_isoline_coeff_7 value="-0.2105379353246843"/>
        <eta_ad_isoline_coeff_8 value="1.566870475061208e-05"/>
        <eta_ad_isoline_coeff_9 value="-2.204687247703566e-10"/>
        <surgeline_coeff_1 value="-32.42061570262501"/>
        <surgeline_coeff_2 value="258.3046890506004"/>
        <surgeline_coeff_3 value="0"/>
        <chokeline_coeff_1 value="-10.81995446249999"/>
        <chokeline_coeff_2 value="7.139917984696915"/>
        <chokeline_coeff_3 value="0"/>
        <efficiencyOfChokeline value="0.4"/>
        <surgelineMeasurements>
          <measurement>
            <speed value="3435" unit="per_min"/>
            <adiabaticHead value="21.67742684868868" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2094350000000046" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="4505.625" unit="per_min"/>
            <adiabaticHead value="28.44736827885277" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2356441309880909" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5576.25" unit="per_min"/>
            <adiabaticHead value="35.21431372797957" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2618416633441574" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="6646.875" unit="per_min"/>
            <adiabaticHead value="41.97866493312883" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2880291523518547" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="7717.5" unit="per_min"/>
            <adiabaticHead value="48.74082209270989" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3142081473381068" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="8788.125" unit="per_min"/>
            <adiabaticHead value="55.50118402816811" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3403801922990633" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="9858.75" unit="per_min"/>
            <adiabaticHead value="62.26014834400559" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3665468265196037" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="10929.375" unit="per_min"/>
            <adiabaticHead value="69.01811158631355" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3927095851870784" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="12000" unit="per_min"/>
            <adiabaticHead value="75.77546940000067" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.4188700000000027" unit="m_cube_per_s"/>
          </measurement>
        </surgelineMeasurements>
        <characteristicDiagramMeasurements>
          <adiabaticEfficiency value="0.785">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="21.18876653430678" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4059747562954595" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="27.78344614424344" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4731873702784596" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="34.35579351483689" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.5401723752992155" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="40.90858214328988" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6069580386895609" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="47.44451095981569" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6735718677986501" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="53.96621299093765" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7400406982888335" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="60.47626346773139" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8063907767744184" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="66.9771874524337" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8726478385516501" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="73.47146704928679" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9388371810912421" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.79">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="20.26549030520309" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.627171012839932" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="26.51755806086106" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7382071272412229" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="32.71101627033711" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8482023418107784" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="38.85406097587003" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9573022174604805" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="44.95432410623089" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.065642296501969" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="51.01896125074374" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.173349661504698" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="57.05472694211009" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.280544272311569" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="63.06803990492628" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.38734012484624" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="69.0650402250392" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.493846266435321" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.795">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="18.80473880431311" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.868853581480341" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="24.53573885598781" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.023504486451914" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="30.16454291168723" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.175397634815646" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="35.70807507324596" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.324989723071439" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="41.18121738465413" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.472682342835095" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="46.59723553262999" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.618833468358497" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="51.96810970533836" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.763766384744544" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="57.30479654190239" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.907776756648717" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="62.6174403447026" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.051138327838127" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.8">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="16.75559025815912" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.123436151041296" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="21.81541431346995" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.318129878307748" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="26.73750698058301" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.507523927752071" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="31.54874055292691" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.692652301132157" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="36.2713744613232" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.874371504821765" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="40.92426546721138" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.053407116060084" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="45.52372261212646" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.230386680004787" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="50.08412935261953" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.405863648462953" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="54.61840891621819" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.580335286024844" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.7000000000000001">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="14.1455733394535" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.381353083372442" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="18.44490452786024" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.61005143362123" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="22.59028931236075" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.830560768635504" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="26.61606504229204" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.044707627195635" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="30.54920341326131" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.253926739965177" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="34.41158159983944" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.459381839979156" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="38.22146059626435" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.662044301405577" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="41.99448881033254" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.862746524655165" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="45.74440925992412" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.062219554948419" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.6000000000000001">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="11.0761033857033" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.633366779705666" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="14.59405774397458" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.889148944471877" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="17.96253028725465" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.134062639002898" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="21.21836381364166" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.370786616259643" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="24.38931450299298" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.601338962620314" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="27.49717029075599" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.827303827487365" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="30.55965609903784" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.049969948145355" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="33.59166187818781" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.270419937768227" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="36.60607140570961" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.489590545433616" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.5">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="7.690025852822286" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.872432635975637" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="10.45909460750275" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.148850147599437" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="13.09798624076916" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.412272952641536" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="15.64116368211469" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.666141253587942" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="18.11382697323992" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.91297060112981" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="20.53531830946768" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.154691796548774" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="22.9211104425056" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.392849380592612" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="25.28404308205845" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.62872505513332" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="27.63513340405706" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.863418590752896" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.4">
            <measurement>
              <speed value="3435" unit="per_min"/>
              <adiabaticHead value="4.133532768750003" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.09435" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4505.625" unit="per_min"/>
              <adiabaticHead value="6.216633328328443" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.38610412995544" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5576.25" unit="per_min"/>
              <adiabaticHead value="8.196307563366203" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.663372613890524" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6646.875" unit="per_min"/>
              <adiabaticHead value="10.10136183577575" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.930190002618613" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7717.5" unit="per_min"/>
              <adiabaticHead value="11.95244893997314" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.18944887760357" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8788.125" unit="per_min"/>
              <adiabaticHead value="13.76519780688789" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.443338189889796" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9858.75" unit="per_min"/>
              <adiabaticHead value="15.55198658398167" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.69359159348959" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10929.375" unit="per_min"/>
              <adiabaticHead value="17.32301952986488" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.94163827269222" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="19.08702" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.188700000000001" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
        </characteristicDiagramMeasurements>
      </turboCompressor>
    </compressors>
    <drives>
      <gasTurbine id="drive_5">
        <energy_rate_fun_coeff_1 value="4635.09742"/>
        <energy_rate_fun_coeff_2 value="2.88577"/>
        <energy_rate_fun_coeff_3 value="-2.85112e-18"/>
        <power_fun_coeff_1 value="-1713.308037005128"/>
        <power_fun_coeff_2 value="3.007553535928011"/>
        <power_fun_coeff_3 value="-9.882462272569154e-05"/>
        <power_fun_coeff_4 value="10.30657581224263"/>
        <power_fun_coeff_5 value="-0.01809223902410705"/>
        <power_fun_coeff_6 value="5.944893995939196e-07"/>
        <power_fun_coeff_7 value="-0.03425564373857679"/>
        <power_fun_coeff_8 value="6.013260909669014e-05"/>
        <power_fun_coeff_9 value="-1.975885827634402e-09"/>
      </gasTurbine>
      <gasTurbine id="drive_6">
        <energy_rate_fun_coeff_1 value="1925.34811"/>
        <energy_rate_fun_coeff_2 value="2.66198"/>
        <energy_rate_fun_coeff_3 value="2.22172e-19"/>
        <power_fun_coeff_1 value="-1446.65293318235"/>
        <power_fun_coeff_2 value="2.539465204434912"/>
        <power_fun_coeff_3 value="-8.344379834151966e-05"/>
        <power_fun_coeff_4 value="8.702485372046633"/>
        <power_fun_coeff_5 value="-0.01527640686132047"/>
        <power_fun_coeff_6 value="5.019645125646392e-07"/>
        <power_fun_coeff_7 value="-0.02892417850270868"/>
        <power_fun_coeff_8 value="5.077371578884042e-05"/>
        <power_fun_coeff_9 value="-1.668363753885891e-09"/>
      </gasTurbine>
    </drives>
    <configurations>
      <configuration nrOfSerialStages="1" confId="config_1">
        <stage nrOfParallelUnits="1" stageNr="1">
          <compressor nominalSpeed="10000" id="compressor_5"/>
        </stage>
      </configuration>
      <configuration nrOfSerialStages="1" confId="config_2">
        <stage nrOfParallelUnits="1" stageNr="1">
          <compressor nominalSpeed="10000" id="compressor_6"/>
        </stage>
      </configuration>
    </configurations>
  </compressorStation>
  <compressorStation id="compressorStation_3">
    <compressors>
      <turboCompressor drive="drive_7" id="compressor_7">
        <speedMin value="3430" unit="per_min"/>
        <speedMax value="12000" unit="per_min"/>
        <n_isoline_coeff_1 value="0"/>
        <n_isoline_coeff_2 value="0.003135764166666667"/>
        <n_isoline_coeff_3 value="0"/>
        <n_isoline_coeff_4 value="0"/>
        <n_isoline_coeff_5 value="0"/>
        <n_isoline_coeff_6 value="0"/>
        <n_isoline_coeff_7 value="-0.5057148788926593"/>
        <n_isoline_coeff_8 value="1.053572664359707e-05"/>
        <n_isoline_coeff_9 value="0"/>
        <eta_ad_isoline_coeff_1 value="0.8627491855797049"/>
        <eta_ad_isoline_coeff_2 value="-4.051214273591674e-05"/>
        <eta_ad_isoline_coeff_3 value="2.120564473688459e-09"/>
        <eta_ad_isoline_coeff_4 value="0.0170826181758688"/>
        <eta_ad_isoline_coeff_5 value="3.059701891996469e-05"/>
        <eta_ad_isoline_coeff_6 value="-2.046648723952788e-09"/>
        <eta_ad_isoline_coeff_7 value="-0.05862436710553696"/>
        <eta_ad_isoline_coeff_8 value="4.271145116725125e-06"/>
        <eta_ad_isoline_coeff_9 value="-5.535595757849716e-11"/>
        <surgeline_coeff_1 value="-16.01031030280209"/>
        <surgeline_coeff_2 value="61.85631987920484"/>
        <surgeline_coeff_3 value="0"/>
        <chokeline_coeff_1 value="-5.366076430208331"/>
        <chokeline_coeff_2 value="1.712655799931408"/>
        <chokeline_coeff_3 value="0"/>
        <efficiencyOfChokeline value="0.3"/>
        <surgelineMeasurements>
          <measurement>
            <speed value="3430" unit="per_min"/>
            <adiabaticHead value="10.668320461099" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.4313000000000007" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="4501.25" unit="per_min"/>
            <adiabaticHead value="14.00693526096847" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.4852737056195596" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5572.5" unit="per_min"/>
            <adiabaticHead value="17.34407386931459" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.5392235463935178" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="6643.75" unit="per_min"/>
            <adiabaticHead value="20.6799343996586" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.5931527251234906" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="7715.000000000001" unit="per_min"/>
            <adiabaticHead value="24.01471420734588" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.6470644323540461" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="8786.25" unit="per_min"/>
            <adiabaticHead value="27.34860996927924" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.7009618476617123" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="9857.5" unit="per_min"/>
            <adiabaticHead value="30.68181776282783" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.7548481409306588" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="10928.75" unit="per_min"/>
            <adiabaticHead value="34.01453314400528" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.8087264736165621" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="12000" unit="per_min"/>
            <adiabaticHead value="37.34695122499959" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.8625999999999933" unit="m_cube_per_s"/>
          </measurement>
        </surgelineMeasurements>
        <characteristicDiagramMeasurements>
          <adiabaticEfficiency value="0.7825">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="10.42737783951128" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8361369463934183" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="13.67961677299545" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9745286346428728" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="16.92085536544906" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.112452228205045" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="20.15246072384584" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.24996590123195" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="23.37576323831802" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.387126265473279" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="26.59206084959781" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.523988551867731" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="29.80262304328503" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.660606780510067" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="33.00869460708125" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.797033920531723" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="36.21149918341889" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.933322041274929" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.785">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="9.972173088008248" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.291711074584781" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="13.05557736758325" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.520319877303996" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="16.11011437838177" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.746788411944685" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="19.13982269050188" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.971416104917109" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="22.14846320656603" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.194481795895767" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="25.13956236357678" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.416246940877965" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="28.11644919145765" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.636958359766652" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="31.08228743628333" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.856850618040975" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="34.04010370965295" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.076148113798372" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.7875000000000001">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="9.252055922777313" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.789430292725591" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="12.07870527170697" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.107825180051285" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="14.85501805926539" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.42055013743246" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="17.5893316606591" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.728544290070644" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="20.28897849262874" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.032633564253034" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="22.96049544499749" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.333554277803946" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="25.60978668586457" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.63197147852544" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="28.24225258370351" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.928493466032856" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="30.86289367819991" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.223683503070602" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.79">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="8.241970948353146" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.31367935235956" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="10.73790577926092" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.714512536619312" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="13.16599167811469" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.104449561593552" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="15.53946634744446" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.485616328324116" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="17.86929726773602" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.859774152880634" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="20.16477702935781" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.22841537334072" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="22.43394402196663" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.592830910157325" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="24.68388863917638" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.954159440917189" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="26.92098237197121" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.313424191462601" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.6675">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="6.955497584257586" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.844776481805216" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="9.076689407868987" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.315627493347826" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="11.12202621026931" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.769640605993102" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="13.10842573187849" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.210571130835999" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="15.04917981876754" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.641369522002423" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="16.95507191342707" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.064429431376232" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="18.83510468677116" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.481749224526865" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="20.69699413677278" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.895041658127335" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="22.54751784872843" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.305811184937245" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.545">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="5.442595141324042" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.363716983856653" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="7.178714095581452" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.890347771650466" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="8.841153514015566" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.394628759103839" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="10.44807118592822" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.882067893043327" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="12.01315004761093" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.356815727496842" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="13.54713319948345" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.822131052666251" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="15.05876206430189" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.280665473927556" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="16.55538125816376" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.734646892169683" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="18.04334691693129" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.186003364700136" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.4225">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="3.773625798965965" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.856006584395941" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="5.140636737820282" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.425147608925768" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="6.443456150580847" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.967563148026964" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="7.699076408731981" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.490327801792987" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="8.91992585551071" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.998615983830986" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="10.11554587549461" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.496400152033993" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="11.29357055379956" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.986858679669342" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="12.46033599981637" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.472629541085086" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="13.62127987835844" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.955976652417516" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.3">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="2.020608034895834" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.313000000000001" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="3.049476541937244" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.913744473631314" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="4.027315913535686" unit="kJ_per_kg"/>
              <volumetricFlowrate value="5.484693622688354" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="4.968337938261808" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.034145546865886" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="5.882734305492502" unit="kJ_per_kg"/>
              <volumetricFlowrate value="6.5680510562317" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="6.778219152431898" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.090914346669428" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="7.660903240224442" unit="kJ_per_kg"/>
              <volumetricFlowrate value="7.606303421244656" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="8.535825028190695" unit="kJ_per_kg"/>
              <volumetricFlowrate value="8.117160178335773" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="9.407292499999993" unit="kJ_per_kg"/>
              <volumetricFlowrate value="8.625999999999998" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
        </characteristicDiagramMeasurements>
      </turboCompressor>
      <turboCompressor drive="drive_8" id="compressor_8">
        <speedMin value="3430" unit="per_min"/>
        <speedMax value="12000" unit="per_min"/>
        <n_isoline_coeff_1 value="0"/>
        <n_isoline_coeff_2 value="0.006355286666666667"/>
        <n_isoline_coeff_3 value="0"/>
        <n_isoline_coeff_4 value="0"/>
        <n_isoline_coeff_5 value="0"/>
        <n_isoline_coeff_6 value="0"/>
        <n_isoline_coeff_7 value="-4.346682088207302"/>
        <n_isoline_coeff_8 value="9.055587683765212e-05"/>
        <n_isoline_coeff_9 value="0"/>
        <eta_ad_isoline_coeff_1 value="0.8464679931365099"/>
        <eta_ad_isoline_coeff_2 value="-3.382368229859264e-05"/>
        <eta_ad_isoline_coeff_3 value="1.775953207335171e-09"/>
        <eta_ad_isoline_coeff_4 value="0.05047400560668903"/>
        <eta_ad_isoline_coeff_5 value="5.014714402839382e-05"/>
        <eta_ad_isoline_coeff_6 value="-3.425567304722418e-09"/>
        <eta_ad_isoline_coeff_7 value="-0.2104693729153418"/>
        <eta_ad_isoline_coeff_8 value="1.566463728485779e-05"/>
        <eta_ad_isoline_coeff_9 value="-2.205843702235369e-10"/>
        <surgeline_coeff_1 value="-32.44826657508332"/>
        <surgeline_coeff_2 value="258.1701501064371"/>
        <surgeline_coeff_3 value="0"/>
        <chokeline_coeff_1 value="-10.87548430833333"/>
        <chokeline_coeff_2 value="7.148123357684561"/>
        <chokeline_coeff_3 value="0"/>
        <efficiencyOfChokeline value="0.4"/>
        <surgelineMeasurements>
          <measurement>
            <speed value="3430" unit="per_min"/>
            <adiabaticHead value="21.62159881245805" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2094349999999989" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="4501.25" unit="per_min"/>
            <adiabaticHead value="28.38800502000919" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2356440958414876" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="5572.5" unit="per_min"/>
            <adiabaticHead value="35.15141941446058" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.2618416031507679" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="6643.75" unit="per_min"/>
            <adiabaticHead value="41.91224351460052" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.288029077176532" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="7715.000000000001" unit="per_min"/>
            <adiabaticHead value="48.67087730261102" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3142080672155589" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="8786.25" unit="per_min"/>
            <adiabaticHead value="55.42771938566716" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.340380117238656" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="9857.5" unit="per_min"/>
            <adiabaticHead value="62.1831671558616" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3665467665101126" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="10928.75" unit="per_min"/>
            <adiabaticHead value="68.93761694865555" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.3927095502014466" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="12000" unit="per_min"/>
            <adiabaticHead value="75.69146419999929" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.4188699999999972" unit="m_cube_per_s"/>
          </measurement>
        </surgelineMeasurements>
        <characteristicDiagramMeasurements>
          <adiabaticEfficiency value="0.785">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="21.13327783262032" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4060198037744166" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="27.72462515092226" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4732214342602127" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="34.29367796078419" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.5401957626109979" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="40.84320699248406" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6069710376176981" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="47.37590856188599" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6735747493841759" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="53.89441321930967" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7400337175061861" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="60.40129384475362" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8063741736056714" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="66.89907326272325" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8726218389672197" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="73.39023144238134" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9388019979467063" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.79">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="20.21070950985446" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.627242079540142" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="26.45987783514873" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7382522455440816" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="32.65054055906241" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8482231186080103" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="38.79088269466818" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9573000972253988" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="44.88852650340564" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.065618583175122" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="50.95061905274275" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.173305536894915" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="56.98390732311603" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.280480811680335" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="62.99480331242343" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.38725831020035" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="68.98944108665938" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.493746997944264" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.795">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="18.75124037398042" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8689295927590638" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="24.48004074409582" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.023538990456854" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="30.10682346864687" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.175395126439061" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="35.64848599484855" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.324954030584153" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="41.11988900987936" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.472616764501122" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="46.53428089803313" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.618740876818618" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="51.90362769974017" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.763649308149724" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="57.23887439935871" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.907637442751196" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="62.55015564397983" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.050978795422192" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.8">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="16.70409038789516" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.123499733738522" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="21.76262811861962" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.318140350352111" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="26.68365569541925" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.507489900144553" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="31.49400211113746" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.692580699565411" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="36.21589527539805" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.874268026219698" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="40.86816858016817" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.053276544668708" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="45.4671135154618" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.230233113073961" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="50.02710025760622" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.405690661971925" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="54.56104197530487" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.580146059677648" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.7000000000000001">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="14.09678110591259" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.381395229461802" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="18.39582318864997" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.61003580818294" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="22.54112909121569" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.830500070290204" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="26.56698617847725" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.044611557585526" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="30.50033317656991" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.253802981313651" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="34.36302500335061" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.459236675076006" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="38.17330746793755" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.661883025362357" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="41.94681866568203" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.862573729816597" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="45.69729480095972" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.062039335769377" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.6000000000000001">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="11.03056559591023" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.633387587558586" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="14.54917638910267" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.889114272097416" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="17.91846008155149" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.133988115378883" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="21.17521725841324" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.370683721723926" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="24.34717927254238" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.601216558980528" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="27.45611928009077" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.827169063332149" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="30.5197536157498" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.049828828036212" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="33.55296769126443" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.270277699655826" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="36.56864355494885" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.489451923686467" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.5">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="7.648047637029807" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.872438532350948" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="10.41858328037936" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.148807765998999" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="13.05902127345496" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.412199369132918" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="15.60380023669794" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.666048697353384" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="18.07810882584414" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.912868394559802" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="20.50128466673674" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.154587446884395" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="22.88879984106638" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.392749240845233" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="25.253495809284" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.628634750607825" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="27.60639314463743" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.863343311382014" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.4">
            <measurement>
              <speed value="3430" unit="per_min"/>
              <adiabaticHead value="4.095187845833333" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.09435" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="4501.25" unit="per_min"/>
              <adiabaticHead value="6.180406617723387" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.386065554915312" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="5572.5" unit="per_min"/>
              <adiabaticHead value="8.162204096794428" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.663312795890877" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="6643.75" unit="per_min"/>
              <adiabaticHead value="10.0693834664531" unit="kJ_per_kg"/>
              <volumetricFlowrate value="2.930121197792387" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="7715.000000000001" unit="per_min"/>
              <adiabaticHead value="11.9226003322122" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.189380414935975" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8786.25" unit="per_min"/>
              <adiabaticHead value="13.73748901818299" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.443277640145401" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="9857.5" unit="per_min"/>
              <adiabaticHead value="15.52643426912319" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.693545460302282" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10928.75" unit="per_min"/>
              <adiabaticHead value="17.29964758425231" unit="kJ_per_kg"/>
              <volumetricFlowrate value="3.941612432065274" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12000" unit="per_min"/>
              <adiabaticHead value="19.06585999999999" unit="kJ_per_kg"/>
              <volumetricFlowrate value="4.1887" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
        </characteristicDiagramMeasurements>
      </turboCompressor>
    </compressors>
    <drives>
      <gasTurbine id="drive_7">
        <energy_rate_fun_coeff_1 value="4635.09742"/>
        <energy_rate_fun_coeff_2 value="2.88577"/>
        <energy_rate_fun_coeff_3 value="-2.85112e-18"/>
        <power_fun_coeff_1 value="-1717.747960761075"/>
        <power_fun_coeff_2 value="3.015347410761396"/>
        <power_fun_coeff_3 value="-9.908072015863145e-05"/>
        <power_fun_coeff_4 value="10.3332846175496"/>
        <power_fun_coeff_5 value="-0.01813912385748577"/>
        <power_fun_coeff_6 value="5.96029979309246e-07"/>
        <power_fun_coeff_7 value="-0.03434441495958621"/>
        <power_fun_coeff_8 value="6.02884387512934e-05"/>
        <power_fun_coeff_9 value="-1.981006204260014e-09"/>
      </gasTurbine>
      <gasTurbine id="drive_8">
        <energy_rate_fun_coeff_1 value="1925.34811"/>
        <energy_rate_fun_coeff_2 value="2.66198"/>
        <energy_rate_fun_coeff_3 value="2.22172e-19"/>
        <power_fun_coeff_1 value="-1444.283664465272"/>
        <power_fun_coeff_2 value="2.535306172694149"/>
        <power_fun_coeff_3 value="-8.330713751810448e-05"/>
        <power_fun_coeff_4 value="8.688232799173154"/>
        <power_fun_coeff_5 value="-0.01525138779001755"/>
        <power_fun_coeff_6 value="5.011424157165126e-07"/>
        <power_fun_coeff_7 value="-0.02887680767192974"/>
        <power_fun_coeff_8 value="5.069056068390198e-05"/>
        <power_fun_coeff_9 value="-1.665631376298896e-09"/>
      </gasTurbine>
    </drives>
    <configurations>
      <configuration nrOfSerialStages="1" confId="config_1">
        <stage nrOfParallelUnits="1" stageNr="1">
          <compressor nominalSpeed="12000" id="compressor_7"/>
        </stage>
      </configuration>
      <configuration nrOfSerialStages="1" confId="config_2">
        <stage nrOfParallelUnits="1" stageNr="1">
          <compressor nominalSpeed="12000" id="compressor_8"/>
        </stage>
      </configuration>
    </configurations>
  </compressorStation>
  <compressorStation id="compressorStation_4">
    <compressors>
      <turboCompressor drive="drive_9" id="compressor_9">
        <speedMin value="7865.000000000001" unit="per_min"/>
        <speedMax value="16517" unit="per_min"/>
        <n_isoline_coeff_1 value="0"/>
        <n_isoline_coeff_2 value="0.002976001089786281"/>
        <n_isoline_coeff_3 value="0"/>
        <n_isoline_coeff_4 value="0"/>
        <n_isoline_coeff_5 value="0"/>
        <n_isoline_coeff_6 value="0"/>
        <n_isoline_coeff_7 value="-12.45749844411187"/>
        <n_isoline_coeff_8 value="0.0001885557069097273"/>
        <n_isoline_coeff_9 value="0"/>
        <eta_ad_isoline_coeff_1 value="0.8558933277178956"/>
        <eta_ad_isoline_coeff_2 value="-9.615448119206385e-06"/>
        <eta_ad_isoline_coeff_3 value="2.943812677462944e-10"/>
        <eta_ad_isoline_coeff_4 value="0.1597086019812639"/>
        <eta_ad_isoline_coeff_5 value="1.887731817637502e-05"/>
        <eta_ad_isoline_coeff_6 value="-9.3898603864169e-10"/>
        <eta_ad_isoline_coeff_7 value="-0.5315200312994284"/>
        <eta_ad_isoline_coeff_8 value="3.318695906665943e-05"/>
        <eta_ad_isoline_coeff_9 value="-6.185029652919177e-10"/>
        <surgeline_coeff_1 value="-2.18996852194784"/>
        <surgeline_coeff_2 value="256.6246423023954"/>
        <surgeline_coeff_3 value="0"/>
        <chokeline_coeff_1 value="-8.44590274436074"/>
        <chokeline_coeff_2 value="10.43825777505071"/>
        <chokeline_coeff_3 value="0"/>
        <efficiencyOfChokeline value="0.6"/>
        <surgelineMeasurements>
          <measurement>
            <speed value="7865.000000000001" unit="per_min"/>
            <adiabaticHead value="23.29799095152627" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.09932000000000075" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="8946.5" unit="per_min"/>
            <adiabaticHead value="26.49026720004719" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.1117594766608558" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="10028" unit="per_min"/>
            <adiabaticHead value="29.68036642019461" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.1241904700039983" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="11109.5" unit="per_min"/>
            <adiabaticHead value="32.86848108712135" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.136613730055424" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="12191" unit="per_min"/>
            <adiabaticHead value="36.05480257881349" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.1490300025657526" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="13272.5" unit="per_min"/>
            <adiabaticHead value="39.23952125655726" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.1614400293237871" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="14354" unit="per_min"/>
            <adiabaticHead value="42.42282654419381" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.1738445484653491" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="15435.5" unit="per_min"/>
            <adiabaticHead value="45.6049070062441" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.1862442947777108" unit="m_cube_per_s"/>
          </measurement>
          <measurement>
            <speed value="16517" unit="per_min"/>
            <adiabaticHead value="48.78595042500007" unit="kJ_per_kg"/>
            <volumetricFlowrate value="0.1986400000000003" unit="m_cube_per_s"/>
          </measurement>
        </surgelineMeasurements>
        <characteristicDiagramMeasurements>
          <adiabaticEfficiency value="0.8325">
            <measurement>
              <speed value="7865.000000000001" unit="per_min"/>
              <adiabaticHead value="22.7702245405204" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.2407377717599407" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8946.5" unit="per_min"/>
              <adiabaticHead value="25.85788160761108" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.2668413716837612" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10028" unit="per_min"/>
              <adiabaticHead value="28.936989676132" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.2928726968589405" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="11109.5" unit="per_min"/>
              <adiabaticHead value="32.00842460896161" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.3188391519854406" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12191" unit="per_min"/>
              <adiabaticHead value="35.07304219781681" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.3447479720780673" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="13272.5" unit="per_min"/>
              <adiabaticHead value="38.1316800494554" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.3706062384127603" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="14354" unit="per_min"/>
              <adiabaticHead value="41.18515936739473" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.3964208935895581" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="15435.5" unit="per_min"/>
              <adiabaticHead value="44.23428664039387" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4221987558073256" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="16517" unit="per_min"/>
              <adiabaticHead value="47.27985524793621" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4479465324367883" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.835">
            <measurement>
              <speed value="7865.000000000001" unit="per_min"/>
              <adiabaticHead value="21.68352216443217" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.3962010566787121" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8946.5" unit="per_min"/>
              <adiabaticHead value="24.57450534343769" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4363026346420901" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10028" unit="per_min"/>
              <adiabaticHead value="27.44761461958549" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.4761562790601732" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="11109.5" unit="per_min"/>
              <adiabaticHead value="30.304972735325" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.515791435044386" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12191" unit="per_min"/>
              <adiabaticHead value="33.14859726955734" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.5552360889552811" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="13272.5" unit="per_min"/>
              <adiabaticHead value="35.98041359704468" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.5945169481658714" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="14354" unit="per_min"/>
              <adiabaticHead value="38.80226645098837" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6336596014491499" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="15435.5" unit="per_min"/>
              <adiabaticHead value="41.61593030420671" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.6726886629781026" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="16517" unit="per_min"/>
              <adiabaticHead value="44.42311875009189" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.711627902451396" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.8374999999999999">
            <measurement>
              <speed value="7865.000000000001" unit="per_min"/>
              <adiabaticHead value="19.96415879132972" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.5600393862301182" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8946.5" unit="per_min"/>
              <adiabaticHead value="22.57342613289543" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.613311606869596" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10028" unit="per_min"/>
              <adiabaticHead value="25.15591145789781" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.666037031298197" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="11109.5" unit="per_min"/>
              <adiabaticHead value="27.7153106009152" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7182911156840069" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12191" unit="per_min"/>
              <adiabaticHead value="30.25502516720664" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7701433090493626" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="13272.5" unit="per_min"/>
              <adiabaticHead value="32.77820868751442" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8216579955923954" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="14354" unit="per_min"/>
              <adiabaticHead value="35.28780541514757" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8728952867893799" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="15435.5" unit="per_min"/>
              <adiabaticHead value="37.78658327018514" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9239116940015" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="16517" unit="per_min"/>
              <adiabaticHead value="40.27716210024553" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9747607054620789" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.84">
            <measurement>
              <speed value="7865.000000000001" unit="per_min"/>
              <adiabaticHead value="17.6367114883861" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7250666979383555" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8946.5" unit="per_min"/>
              <adiabaticHead value="19.90728682400939" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.7897405156729442" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10028" unit="per_min"/>
              <adiabaticHead value="22.14586935131037" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.853503067869767" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="11109.5" unit="per_min"/>
              <adiabaticHead value="24.35750664540168" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9164981268792566" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12191" unit="per_min"/>
              <adiabaticHead value="26.54670602806683" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9788540767734688" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="13272.5" unit="per_min"/>
              <adiabaticHead value="28.71753639995153" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.040686813878156" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="14354" unit="per_min"/>
              <adiabaticHead value="30.87370941649622" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.102102058943332" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="15435.5" unit="per_min"/>
              <adiabaticHead value="33.01864514931408" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.163197227405817" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="16517" unit="per_min"/>
              <adiabaticHead value="35.15552596177238" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.22406296395163" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.78">
            <measurement>
              <speed value="7865.000000000001" unit="per_min"/>
              <adiabaticHead value="14.81921152214556" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.8845637595230866" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8946.5" unit="per_min"/>
              <adiabaticHead value="16.7302640332864" unit="kJ_per_kg"/>
              <volumetricFlowrate value="0.9584687024760113" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10028" unit="per_min"/>
              <adiabaticHead value="18.60883178662044" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.031117382632098" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="11109.5" unit="per_min"/>
              <adiabaticHead value="20.46063293569062" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.102730934580229" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12191" unit="per_min"/>
              <adiabaticHead value="22.29065125996009" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.173502092918105" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="13272.5" unit="per_min"/>
              <adiabaticHead value="24.10329342155" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.243601273744065" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="14354" unit="per_min"/>
              <adiabaticHead value="25.90250918977086" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.313181224025487" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="15435.5" unit="per_min"/>
              <adiabaticHead value="27.69188511501789" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.382380644190961" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="16517" unit="per_min"/>
              <adiabaticHead value="29.47471885249359" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.451327062405306" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.72">
            <measurement>
              <speed value="7865.000000000001" unit="per_min"/>
              <adiabaticHead value="11.67818141469875" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.033762314704186" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8946.5" unit="per_min"/>
              <adiabaticHead value="13.23869205662383" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.114826843908323" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10028" unit="per_min"/>
              <adiabaticHead value="14.76986045029986" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.194367118502338" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="11109.5" unit="per_min"/>
              <adiabaticHead value="16.27731929464778" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.272675742761975" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12191" unit="per_min"/>
              <adiabaticHead value="17.76589425635583" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.350003397706428" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="13272.5" unit="per_min"/>
              <adiabaticHead value="19.23979201282165" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.426568609447337" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="14354" unit="per_min"/>
              <adiabaticHead value="20.70273976578141" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.502564996564335" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="15435.5" unit="per_min"/>
              <adiabaticHead value="22.15809112384911" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.57816677043165" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="16517" unit="per_min"/>
              <adiabaticHead value="23.60890819889956" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.653532999914842" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.6599999999999999">
            <measurement>
              <speed value="7865.000000000001" unit="per_min"/>
              <adiabaticHead value="8.378376384877688" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.170189563310179" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8946.5" unit="per_min"/>
              <adiabaticHead value="9.614906169587242" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.256698449393902" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10028" unit="per_min"/>
              <adiabaticHead value="10.82713488048046" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.341507207545015" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="11109.5" unit="per_min"/>
              <adiabaticHead value="12.0200624397235" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.42496563742257" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12191" unit="per_min"/>
              <adiabaticHead value="13.19792572279001" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.507370155160034" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="13272.5" unit="per_min"/>
              <adiabaticHead value="14.36438634252184" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.588976930929881" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="14354" unit="per_min"/>
              <adiabaticHead value="15.52266721186985" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.670011443012353" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="15435.5" unit="per_min"/>
              <adiabaticHead value="16.67565442222736" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.750675605307672" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="16517" unit="per_min"/>
              <adiabaticHead value="17.8259750844968" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.831153213176531" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
          <adiabaticEfficiency value="0.6">
            <measurement>
              <speed value="7865.000000000001" unit="per_min"/>
              <adiabaticHead value="5.052852210334837" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.2932" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="8946.5" unit="per_min"/>
              <adiabaticHead value="5.998977542834327" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.383840157858613" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="10028" unit="per_min"/>
              <adiabaticHead value="6.926359932314506" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.472684715012278" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="11109.5" unit="per_min"/>
              <adiabaticHead value="7.839083464594799" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.560124932714303" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="12191" unit="per_min"/>
              <adiabaticHead value="8.740587467182865" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.646490303451058" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="13272.5" unit="per_min"/>
              <adiabaticHead value="9.633830856614102" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.732064295651772" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="14354" unit="per_min"/>
              <adiabaticHead value="10.52141017004424" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.817095661283652" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="15435.5" unit="per_min"/>
              <adiabaticHead value="11.40564670040563" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.901806783524268" unit="m_cube_per_s"/>
            </measurement>
            <measurement>
              <speed value="16517" unit="per_min"/>
              <adiabaticHead value="12.28865249999999" unit="kJ_per_kg"/>
              <volumetricFlowrate value="1.9864" unit="m_cube_per_s"/>
            </measurement>
          </adiabaticEfficiency>
        </characteristicDiagramMeasurements>
      </turboCompressor>
    </compressors>
    <drives>
      <gasTurbine id="drive_9">
        <energy_rate_fun_coeff_1 value="4635.09742"/>
        <energy_rate_fun_coeff_2 value="2.88577"/>
        <energy_rate_fun_coeff_3 value="-2.85112e-18"/>
        <power_fun_coeff_1 value="-491.9704536077123"/>
        <power_fun_coeff_2 value="0.6274325031471536"/>
        <power_fun_coeff_3 value="-1.497851947622048e-05"/>
        <power_fun_coeff_4 value="2.959497456367856"/>
        <power_fun_coeff_5 value="-0.003774382960378271"/>
        <power_fun_coeff_6 value="9.010478162856887e-08"/>
        <power_fun_coeff_7 value="-0.009836389151684914"/>
        <power_fun_coeff_8 value="1.254479861974057e-05"/>
        <power_fun_coeff_9 value="-2.994784451053193e-10"/>
      </gasTurbine>
    </drives>
    <configurations>
      <configuration nrOfSerialStages="1" confId="config_1">
        <stage nrOfParallelUnits="1" stageNr="1">
          <compressor nominalSpeed="14154" id="compressor_9"/>
        </stage>
      </configuration>
    </configurations>
  </compressorStation>
</compressorStations>
