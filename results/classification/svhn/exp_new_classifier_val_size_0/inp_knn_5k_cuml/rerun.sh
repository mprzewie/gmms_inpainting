# 2021-05-10 01:26:08.965805
python train_classifier.py --experiment_name=exp_new_classifier_val_size_0/inp_knn_5k_cuml --convar_type=naive --inpainter_type=knn --dataset svhn --batch_size=64 --img_size 32 --mask_train_size 16 --mask_val_size 16 --num_epochs=25 --lr=1e-3 --dump_sample_results --render_every 3 --max_benchmark_batches=-1 --batch_size 48
