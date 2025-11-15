import os
from flask import Flask, render_template, request
import math

app = Flask(__name__)

def format_output(shift, multiplicity, j_values_list, h_count, h_type):
    """出力を指定された形式でフォーマット"""
    formatted_shift = f"{shift:.2f}"
    
    outputs = []
    
    if j_values_list:
        for i, j_values in enumerate(j_values_list):
            j_text = ""
            if j_values:
                j_parts = []
                for j_idx, j_val in enumerate(j_values):
                    if j_val > 0:
                        if j_idx == 0:
                            j_parts.append(f"J = {j_val:.1f}")
                        else:
                            j_parts.append(f"{j_val:.1f}")
                
                if j_parts:
                    j_text = ", " + ", ".join(j_parts) + " Hz"
            
            candidate_text = f"候補 {i+1}: " if len(j_values_list) > 1 else ""
            output = f"{candidate_text}δ {formatted_shift} ({multiplicity}{j_text}, {h_count}H, {h_type})"
            outputs.append(output)
    else:
        output = f"δ {formatted_shift} ({multiplicity}, {h_count}H, {h_type})"
        outputs.append(output)
    
    return outputs

def calculate_nmr(C1, shifts, multiplicity, h_count, h_type):
    """NMR計算のメインロジック"""
    calculated_shift = None
    j_values_list = []
    
    try:
        if multiplicity == "d":
            if shifts[0] is not None and shifts[1] is not None:
                calculated_shift = (shifts[0] + shifts[1]) / 2
                if shifts[0] is not None and shifts[1] is not None:
                    j_val = abs(shifts[0] - shifts[1]) * C1
                    if j_val > 0:
                        j_values_list.append([j_val])
        
        elif multiplicity == "t":
            if (shifts[0] is not None and shifts[1] is not None and 
                shifts[2] is not None):
                part1 = (shifts[0] + shifts[1]) / 2
                part2 = (shifts[1] + shifts[2]) / 2
                calculated_shift = (part1 + part2) / 2
                
                j_candidates = []
                if shifts[0] is not None and shifts[1] is not None:
                    j_val1 = abs(shifts[0] - shifts[1]) * C1
                    if j_val1 > 0:
                        j_candidates.append([j_val1])
                
                if shifts[1] is not None and shifts[2] is not None:
                    j_val2 = abs(shifts[1] - shifts[2]) * C1
                    if j_val2 > 0:
                        j_candidates.append([j_val2])
                
                j_values_list = j_candidates
        
        elif multiplicity in ["q", "dd"]:
            if (shifts[0] is not None and shifts[1] is not None and 
                shifts[2] is not None and shifts[3] is not None):
                part1 = (shifts[0] + shifts[1]) / 2
                part2 = (shifts[2] + shifts[3]) / 2
                calculated_shift = (part1 + part2) / 2
                
                if multiplicity == "dd":
                    j_candidates = []
                    
                    # パターン1
                    pattern1 = []
                    if shifts[0] is not None and shifts[1] is not None:
                        j1 = abs(shifts[0] - shifts[1]) * C1
                        if j1 > 0:
                            pattern1.append(j1)
                    
                    if shifts[0] is not None and shifts[2] is not None:
                        j2 = abs(shifts[0] - shifts[2]) * C1
                        if j2 > 0:
                            pattern1.append(j2)
                    
                    if pattern1:
                        j_candidates.append(pattern1)
                    
                    # パターン2
                    pattern2 = []
                    if shifts[2] is not None and shifts[3] is not None:
                        j1 = abs(shifts[2] - shifts[3]) * C1
                        if j1 > 0:
                            pattern2.append(j1)
                    
                    if shifts[1] is not None and shifts[3] is not None:
                        j2 = abs(shifts[1] - shifts[3]) * C1
                        if j2 > 0:
                            pattern2.append(j2)
                    
                    if pattern2:
                        j_candidates.append(pattern2)
                    
                    # パターン3
                    pattern3 = []
                    if shifts[0] is not None and shifts[1] is not None:
                        j1 = abs(shifts[0] - shifts[1]) * C1
                        if j1 > 0:
                            pattern3.append(j1)
                    
                    if (shifts[0] is not None and shifts[1] is not None and 
                        shifts[2] is not None and shifts[3] is not None):
                        center1 = (shifts[0] + shifts[1]) / 2
                        center2 = (shifts[2] + shifts[3]) / 2
                        j2 = abs(center1 - center2) * C1
                        if j2 > 0:
                            pattern3.append(j2)
                    
                    if pattern3:
                        j_candidates.append(pattern3)
                    
                    j_values_list = j_candidates
        
        elif multiplicity == "quin":
            if (shifts[0] is not None and shifts[1] is not None and 
                shifts[2] is not None and shifts[3] is not None and
                shifts[4] is not None):
                part1 = (shifts[0] + shifts[1]) / 2
                part2 = (shifts[1] + shifts[2]) / 2
                part3 = (shifts[2] + shifts[3]) / 2
                part4 = (shifts[3] + shifts[4]) / 2
                calculated_shift = ((part1 + part2) / 2 + (part3 + part4) / 2) / 2
                
                j_candidates = []
                if shifts[0] is not None and shifts[1] is not None:
                    j1 = abs(shifts[0] - shifts[1]) * C1
                    if j1 > 0:
                        j_candidates.append([j1])
                
                if shifts[1] is not None and shifts[2] is not None:
                    j2 = abs(shifts[1] - shifts[2]) * C1
                    if j2 > 0:
                        j_candidates.append([j2])
                
                if shifts[2] is not None and shifts[3] is not None:
                    j3 = abs(shifts[2] - shifts[3]) * C1
                    if j3 > 0:
                        j_candidates.append([j3])
                
                if shifts[3] is not None and shifts[4] is not None:
                    j4 = abs(shifts[3] - shifts[4]) * C1
                    if j4 > 0:
                        j_candidates.append([j4])
                
                j_values_list = j_candidates
        
        elif multiplicity == "sext":
            if (shifts[0] is not None and shifts[1] is not None and 
                shifts[2] is not None and shifts[3] is not None and
                shifts[4] is not None and shifts[5] is not None):
                part1 = (shifts[0] + shifts[1]) / 2
                part2 = (shifts[2] + shifts[3]) / 2
                part3 = (shifts[4] + shifts[5]) / 2
                calculated_shift = (part1 + part2 + part3) / 3
                
                j_candidates = []
                if shifts[0] is not None and shifts[1] is not None:
                    j1 = abs(shifts[0] - shifts[1]) * C1
                    if j1 > 0:
                        j_candidates.append([j1])
                
                if shifts[1] is not None and shifts[2] is not None:
                    j2 = abs(shifts[1] - shifts[2]) * C1
                    if j2 > 0:
                        j_candidates.append([j2])
                
                if shifts[2] is not None and shifts[3] is not None:
                    j3 = abs(shifts[2] - shifts[3]) * C1
                    if j3 > 0:
                        j_candidates.append([j3])
                
                if shifts[3] is not None and shifts[4] is not None:
                    j4 = abs(shifts[3] - shifts[4]) * C1
                    if j4 > 0:
                        j_candidates.append([j4])
                
                j_values_list = j_candidates
        
        return calculated_shift, j_values_list, None
        
    except Exception as e:
        return None, None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    input_data = {}
    
    if request.method == 'POST':
        try:
            # フォームデータの取得
            C1 = float(request.form.get('mhz', 500))
            h_count = request.form.get('h_count', '1')
            h_type = request.form.get('h_type', 'CH3')
            multiplicity = request.form.get('multiplicity', 'd')
            
            shifts = []
            for i in range(6):
                shift_str = request.form.get(f'shift{i}', '').strip()
                shifts.append(float(shift_str) if shift_str else None)
            
            # 入力データを保存（再表示用）
            input_data = {
                'mhz': C1,
                'h_count': h_count,
                'h_type': h_type,
                'multiplicity': multiplicity,
                'shifts': shifts
            }
            
            # NMR計算の実行
            calculated_shift, j_values_list, calc_error = calculate_nmr(C1, shifts, multiplicity, h_count, h_type)
            
            if calc_error:
                error = calc_error
            elif calculated_shift is not None:
                outputs = format_output(calculated_shift, multiplicity, j_values_list, h_count, h_type)
                result = "\n".join(outputs)
            else:
                error = "計算に必要なデータが不足しています"
                
        except ValueError:
            error = "数値を正しく入力してください"
        except Exception as e:
            error = f"エラーが発生しました: {str(e)}"
    
    return render_template('index.html', 
                         result=result, 
                         error=error,
                         input_data=input_data)

# Vercel用: アプリケーションをapp変数としてエクスポート
app = app